import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import uuid

from svh.annotations import validate_annotation
from svh.corpus import corpus_gate, freeze_corpus, validate_external
from svh.oracle import git, snapshot, verify


def main():
    parser = argparse.ArgumentParser(description="M0 fixture oracle: Docker only")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    oracle = commands.add_parser("verify", help="verify fixture tests, not the complete M0 gate")
    oracle.add_argument("--manifest", type=Path, default=Path("evals/fixtures.json"))
    oracle.add_argument("--output", type=Path, default=Path("notes/runs/fixture-oracle.json"))
    oracle.add_argument("--image", default="svh-eval:local")
    validate = commands.add_parser("validate", help="validate an owner-recorded walkthrough")
    validate.add_argument("annotation", type=Path)
    gate = commands.add_parser("eval-gate", help="revalidate the annotated M0 visual corpus and native oracle evidence")
    gate.add_argument("--annotations", type=Path, default=Path("evals/annotations"))
    gate.add_argument("--output", type=Path, default=Path("notes/runs/m0-gate.json"))
    freeze = commands.add_parser("freeze-eval", help="freeze a passing M0 corpus for later model evaluation")
    freeze.add_argument("--annotations", type=Path, default=Path("evals/annotations"))
    freeze.add_argument("--output", type=Path, default=Path("evals/frozen-m0.json"))
    serve = commands.add_parser("serve", help="run an archived fixture for recording")
    serve.add_argument("--revision", choices=["pre", "post"], default="pre")
    args = parser.parse_args()
    args.root = args.root.resolve()
    if args.command == "validate":
        path = args.root / args.annotation
        if json.loads(path.read_text()).get("format") == "svh.external.v1":
            data = validate_external(args.root, path)
            print(f"Validated media, provenance and raw oracle evidence: {data['id']}")
        else:
            data = validate_annotation(args.root, path)
            print(f"Valid walkthrough structure: {data['id']}; oracle observations not checked")
        return
    if args.command == "freeze-eval":
        paths = sorted((args.root / args.annotations).glob("*.json"))
        report = freeze_corpus(args.root, paths, args.output)
        print(json.dumps({"corpus_sha256": report["corpus_sha256"], "cases": len(paths), "output": str(args.output)}, indent=2))
        return
    if args.command == "eval-gate":
        paths = sorted((args.root / args.annotations).glob("*.json"))
        report = corpus_gate(args.root, paths)
        output = args.root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: value for key, value in report.items() if key != "cases"}, indent=2))
        raise SystemExit(0 if report["passed"] else 1)
    if args.command == "serve":
        manifest = json.loads((args.root / "evals/fixtures.json").read_text())
        commit = git(args.root, "rev-parse", "--verify", manifest[args.revision + "_fix_commit"] + "^{commit}").decode().strip()
        with tempfile.TemporaryDirectory(prefix="svh-recording-") as directory:
            app = Path(directory)
            app.chmod(0o755)
            snapshot(args.root, commit, app)
            print(f"Recording fixture {commit} at http://127.0.0.1:8080", flush=True)
            name = "svh-recording-" + uuid.uuid4().hex
            try:
                process = subprocess.run([
                    "docker", "run", "--rm", "--name", name, "--pull=never", "--init",
                    "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges",
                    "--memory=256m", "--cpus=1", "--pids-limit=64",
                    "--publish", "127.0.0.1:8080:8080", "--mount", f"type=bind,src={app},dst=/app,readonly",
                    "--entrypoint", "python", "svh-eval:local", "-I", "/app/evals/app/app.py",
                    "--host", "0.0.0.0",
                ])
            finally:
                subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)
            raise SystemExit(process.returncode)
        return
    report = verify(args.root, args.root / args.manifest, args.root / args.output, args.image)
    print(json.dumps(report["summary"], indent=2))
    raise SystemExit(0 if report["claims"] and all(item["verified"] for item in report["claims"]) else 1)


if __name__ == "__main__":
    main()
