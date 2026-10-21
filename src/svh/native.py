"""A bounded external-task oracle pilot, not a general agent execution service.

Dataset shell code runs only in Docker, with no host credentials or network.
Only inspected BPMN/Karma rows are supported by this adapter. Its failure-only reporter
needs positive suite-completion and assertion evidence, not an absent failure.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import uuid


TASK = "bpmn-io__bpmn-js-1655"
IMAGE = "swebench/sweb.eval.x86_64.bpmn-io_1776_bpmn-js-1655@sha256:84f2d5f6c527bff4e80d433dfb46a48abee3d7bcddffe5f1149230d9528c05df"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(image, bundle, side, log_path, timeout):
    name = "svh-external-" + uuid.uuid4().hex
    command = [
        "docker", "run", "--rm", "--name", name, "--pull=never",
        "--network=none", "--cap-drop=ALL", "--cap-add=SETUID", "--cap-add=SETGID",
        "--security-opt=no-new-privileges",
        "--memory=4g", "--cpus=2", "--pids-limit=512", "--shm-size=1g",
        "--mount", f"type=bind,src={bundle},dst=/svh,readonly",
        "--entrypoint", "/bin/bash", image, "/svh/launch.sh", side,
    ]
    try:
        with log_path.open("w") as log:
            process = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
        return {"docker_exit_code": process.returncode, "timeout": False}
    except subprocess.TimeoutExpired:
        return {"docker_exit_code": None, "timeout": True}
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=20)


def evidence(log, expected):
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", log)
    exits = re.findall(r"^SVH_TEST_EXIT_CODE:(\d+)$", text, re.M)
    total = re.findall(r"^TOTAL:\s*(.*)$", text, re.M)
    counts = re.findall(r"Executed (\d+) of (\d+)([^\n]*)", text)
    skipped = (re.findall(r"\(skipped (\d+)\)", counts[-1][2]) or ["0"])[-1] if counts else "0"
    complete = bool(counts and int(counts[-1][0]) > 0
                    and int(counts[-1][0]) + int(skipped) == int(counts[-1][1]))
    # Same failure-name extraction as the upstream BPMN parser; keep assertion
    # text separately so infrastructure errors cannot qualify as bug evidence.
    targets = [expected] if isinstance(expected, str) else expected
    lines = text.splitlines()
    # Karma progress uses carriage returns. Searching the entire log makes the
    # lazy wildcard retry across many accumulated progress messages. Match only
    # complete failure headers, once, before attaching assertion details.
    headers = {}
    for index, line in enumerate(lines):
        if line.endswith(' FAILED'):
            header = re.match(r"(?:Chrome Headless|HeadlessChrome).*?\(Linux[^)]*\)\s(.*?)\sFAILED$", line)
            if header:
                headers[index] = header[1].strip()
    failures = set(headers.values())
    target_results = []
    for target in targets:
        excerpt = None
        for index, failure in headers.items():
            if failure == target.strip():
                line = lines[index]
                block = [line]
                for detail in lines[index + 1:]:
                    if re.match(r"(?:Chrome Headless|HeadlessChrome)", detail):
                        break
                    block.append(detail)
                excerpt = "\n".join(block)[:4000]
                break
        target_results.append({
            "name": target,
            "failed": target.strip() in failures,
            "assertion": bool(excerpt and re.search(r"AssertionError|expected .* to (?:equal|eql)", excerpt)),
            "excerpt": excerpt,
        })
    return {
        "test_exit_code": int(exits[-1]) if exits else None,
        "suite_complete": complete,
        "executed": int(counts[-1][0]) if counts else 0,
        "discovered": int(counts[-1][1]) if counts else 0,
        "skipped": int(skipped),
        "expected_failure_observed": bool(target_results) and all(target["failed"] for target in target_results),
        "assertion_observed": bool(target_results) and all(target["assertion"] for target in target_results),
        "summary": total[-1] if total else None,
        "all_passed": bool(total and re.fullmatch(r"[1-9]\d* SUCCESS", total[-1].strip())),
        "base_commit_observed": (re.findall(r"^SVH_BASE_COMMIT:([0-9a-f]{40})$", text, re.M) or [None])[-1],
        "failure_excerpt": target_results[0]["excerpt"] if target_results else None,
        "targets": target_results,
        "log_sha256": sha(log.encode()),
    }


def verified_pair(pre, post, base_commit):
    return (
        not pre["timeout"] and not post["timeout"]
        and pre["docker_exit_code"] == post["docker_exit_code"] == 0
        and pre["base_commit_observed"] == post["base_commit_observed"] == base_commit
        and pre["suite_complete"] and post["suite_complete"]
        and pre["expected_failure_observed"] and pre["assertion_observed"]
        and pre["test_exit_code"] != 0 and pre["test_exit_code"] is not None
        and post["test_exit_code"] == 0 and post["all_passed"]
        and post["executed"] >= pre["executed"]
        and post["discovered"] == pre["discovered"]
        and post["skipped"] == pre["skipped"]
    )


def evaluation_script(row):
    upstream = row["eval_script"]
    match = re.search(r"^git apply -v - <<'([^']+)'$", upstream, re.M)
    if not match:
        raise ValueError("Unexpected upstream test-patch layout")
    delimiter = match[1]
    executed = upstream.replace("\n" + delimiter + "\n", "\n" + delimiter + "\nif [ $? -ne 0 ]; then exit 89; fi\n", 1)
    end = ": '>>>>> End Test Output'"
    if upstream.count(end) != 1:
        raise ValueError("Unexpected upstream evaluation markers")
    executed = executed.replace(end, 'SVH_TEST_EXIT_CODE=$?\necho "SVH_TEST_EXIT_CODE:$SVH_TEST_EXIT_CODE"\n' + end, 1)
    if executed == upstream or executed.count("SVH_TEST_EXIT_CODE=$?") != 1:
        raise ValueError("Unexpected upstream evaluation script layout")
    return executed


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--row", type=Path, default=Path("data/external/swebench-multimodal/bpmn-pilot-row.json"))
    parser.add_argument("--output", type=Path, default=Path("notes/runs/swebench-bpmn-pilot.json"))
    parser.add_argument("--logs", type=Path, default=Path("data/external/swebench-multimodal/pilot-logs"))
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--image", default=IMAGE, help="immutable approved swebench image reference")
    parser.add_argument("--regrade", action="store_true", help="re-evaluate saved logs without rerunning Docker")
    args = parser.parse_args(argv)
    row_bytes = args.row.read_bytes()
    row = json.loads(row_bytes)
    task = row["instance_id"]
    if (not re.fullmatch(r"[A-Za-z0-9_.-]+", task)
            or row["repo"] != "bpmn-io/bpmn-js" or row["log_parser"] != "parse_log_bpmn_js"
            or not row["FAIL_TO_PASS"] or not re.fullmatch(r"[0-9a-f]{40}", row["base_commit"])):
        raise ValueError("This native adapter supports only BPMN/Karma rows with expected failures")
    if not re.fullmatch(r"swebench/[a-z0-9._-]+@sha256:[0-9a-f]{64}", args.image):
        raise ValueError("An immutable swebench image digest is required")
    if row["image_assets"]["test_patch"]:
        raise ValueError("Binary test assets need explicit staging; this pilot does not support them")
    fix_files = set(re.findall(r"^diff --git a/(\S+) b/", row["patch"], re.M))
    test_files = set(re.findall(r"^diff --git a/(\S+) b/", row["test_patch"], re.M))
    if not fix_files or not test_files or fix_files & test_files:
        raise ValueError("The reference fix must not modify the held-out test files")
    args.logs.mkdir(parents=True, exist_ok=True)
    upstream = row["eval_script"]
    # Guard the supplied test patch and capture the test command's own exit code;
    # the original script's final git checkout otherwise hides test failures.
    executed = evaluation_script(row)
    prior = json.loads(args.output.read_text()) if args.regrade else None
    if prior and (prior["row_sha256"] != sha(row_bytes)
                  or prior["executed_eval_sha256"] != sha(executed.encode()) or prior["image"] != args.image):
        raise ValueError("Cannot regrade logs from different source/test inputs")
    image_id = prior["image_id"] if prior else subprocess.check_output(["docker", "image", "inspect", args.image, "--format", "{{.Id}}"], text=True).strip()
    results = {}
    with tempfile.TemporaryDirectory(prefix="svh-external-") as directory:
        bundle = Path(directory)
        bundle.chmod(0o755)
        (bundle / "eval.sh").write_text(executed)
        (bundle / "fix.diff").write_text(row["patch"])
        (bundle / "launch.sh").write_text(
            "set -e\ncd /testbed\ngit config --global --add safe.directory /testbed\n"
            'echo "SVH_BASE_COMMIT:$(git rev-parse HEAD)"\n'
            'if [ "$1" = post ]; then git apply --check /svh/fix.diff; git apply /svh/fix.diff; fi\n'
            "exec /bin/bash /svh/eval.sh\n"
        )
        for side in ["pre", "post"]:
            print(f"Regrading {task} {side} saved log" if prior else f"Running {task} {side} in Docker", flush=True)
            log_path = args.logs / (side + ".log")
            result = ({key: prior["results"][side][key] for key in ("docker_exit_code", "timeout")}
                      if prior else run(image_id, bundle, side, log_path, args.timeout))
            if prior:
                previous = prior["results"][side]
                checksum = sha(log_path.read_bytes()) if "raw_log_sha256" in previous else sha(log_path.read_text(errors="replace").encode())
                if checksum != previous.get("raw_log_sha256", previous["log_sha256"]):
                    raise ValueError("Saved log changed since execution")
            result.update(evidence(log_path.read_text(errors="replace"), row["FAIL_TO_PASS"]))
            result["raw_log_sha256"] = sha(log_path.read_bytes())
            results[side] = result
            print(json.dumps({"side": side, **{key: result[key] for key in ["test_exit_code", "suite_complete", "executed", "skipped", "expected_failure_observed", "assertion_observed", "summary"]}}), flush=True)
    pre, post = results["pre"], results["post"]
    verified = verified_pair(pre, post, row["base_commit"])
    report = {
        "task": task, "run_at": prior["run_at"] if prior else datetime.now(timezone.utc).isoformat(),
        "graded_at": datetime.now(timezone.utc).isoformat(),
        "row_sha256": sha(row_bytes), "image": args.image, "image_id": image_id,
        "base_commit": row["base_commit"], "fix_patch_sha256": sha(row["patch"].encode()),
        "test_patch_sha256": sha(row["test_patch"].encode()),
        "upstream_eval_sha256": sha(upstream.encode()), "executed_eval_sha256": sha(executed.encode()),
        "results": results, "verified": verified,
        "scope": "Supplied test/gold-fix oracle only; no agent-generated reproduction, media-derived claim or full M0 admission yet",
        "raw_logs": str(args.logs),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    raise SystemExit(0 if verified else 1)


if __name__ == "__main__":
    main()
