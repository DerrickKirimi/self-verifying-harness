"""Sequential, resumable oracle curation. No models, cloud jobs or paid APIs."""

import argparse
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import shutil
import subprocess

from svh.native import main as native_main
from svh.sources import export_rows, resolve_image


IDS = [f"bpmn-io__bpmn-js-{number}" for number in
       [1557, 1567, 1570, 1578, 1610, 1623, 1638, 1655, 1659, 1677, 1679, 1719]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rerun", action="store_true", help="run fresh Docker evaluations instead of regrading saved logs")
    args = parser.parse_args()
    source = Path("data/external/swebench-multimodal").resolve()
    report_root = Path("notes/runs/native")
    report_root.mkdir(parents=True, exist_ok=True)
    progress_path = Path("notes/runs/m0-curation-progress.json")
    progress = json.loads(progress_path.read_text()) if progress_path.exists() else {"cases": {}}
    selected = export_rows(source, IDS)

    def save():
        progress["updated_at"] = datetime.now(timezone.utc).isoformat()
        temporary = progress_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(progress, indent=2) + "\n")
        temporary.replace(progress_path)

    for task in IDS:
        row = selected[task]
        case = progress["cases"].setdefault(task, {})
        output = report_root / (task + ".json")
        row_path = source / "cases" / (task + ".json")
        if task == "bpmn-io__bpmn-js-1655":
            output = Path("notes/runs/swebench-bpmn-pilot.json")
            row_path = source / "bpmn-pilot-row.json"
            if not row_path.exists():
                row_path.write_text(json.dumps(row, indent=2) + "\n")
            if json.loads(row_path.read_text()) != row:
                raise ValueError("Original pilot row differs from pinned source")
        case["report"] = str(output)
        case["row"] = str(row_path.relative_to(Path.cwd()))
        # Existing reports still get log/source validation; absence of a process
        # handle alone is never treated as proof of a completed run.
        reuse = output.exists() and not args.rerun
        if output.exists():
            prior = json.loads(output.read_text())
            case.update(state="regrading" if reuse else "preparing-rerun", image=prior["image"])
        else:
            case["state"] = "resolving-image"
            save()
            case["image"] = resolve_image(row["image"])
        save()
        image = case["image"]
        if not reuse:
            if shutil.disk_usage(source).free < 15 * 1024 ** 3:
                case.update(state="deferred", reason="Less than 15 GiB free; preserve owner data")
                save()
                break
            case["state"] = "pulling-image"
            save()
            print(task, "pulling", image, flush=True)
            result = subprocess.run(["docker", "pull", image], stdout=subprocess.DEVNULL,
                                    stderr=subprocess.PIPE, text=True, timeout=900)
            if result.returncode:
                case.update(state="image-error", detail=result.stderr[-2000:])
                save()
                continue
        native_args = ["--row", str(row_path), "--image", image,
                "--output", str(output), "--logs", str(source / "cases" / task / "logs")]
        if reuse:
            native_args.append("--regrade")
        case["state"] = "running-oracle"
        save()
        try:
            native_main(native_args)
        except SystemExit as result:
            case["state"] = "oracle-passed" if result.code == 0 else "oracle-rejected"
        except Exception as error:
            case.update(state="error", detail=type(error).__name__ + ": " + str(error))
        save()
        print(task, case["state"], flush=True)


if __name__ == "__main__":
    lock_path = Path("data/external/m0-curation.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("An M0 curation batch already holds the process lock")
        main()
