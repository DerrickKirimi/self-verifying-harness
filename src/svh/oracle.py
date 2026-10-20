"""M0 gate runner. Candidate code executes only in restricted Docker containers."""

from datetime import datetime, timezone
import hashlib
import io
import json
from math import sqrt
from pathlib import Path
import subprocess
import tarfile
import tempfile
import uuid
import xml.etree.ElementTree as ET


def wilson(successes, total):
    if total == 0:
        return [0.0, 1.0]
    z = 1.959963984540054
    p = successes / total
    scale = 1 + z * z / total
    center = (p + z * z / (2 * total)) / scale
    half = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / scale
    return [max(0.0, center - half), min(1.0, center + half)]


def classify(result):
    """Require one executed assertion test; crashes/collection errors never count."""
    try:
        root = ET.fromstring(result["junit"])
        cases = list(root.iter("testcase"))
        if len(cases) != 1 or list(root.iter("error")) or list(root.iter("skipped")):
            return "error"
        failures = list(root.iter("failure"))
        if result["exit_code"] == 0 and not failures:
            return "pass"
        if result["exit_code"] == 1 and len(failures) == 1:
            if failures[0].get("message", "").startswith(("assert ", "AssertionError: assert ")):
                return "assertion_failure"
    except (ET.ParseError, TypeError, KeyError):
        pass
    return "error"


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def contained(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"path escapes approved root: {relative}")
    return path


def snapshot(root, commit, target):
    """Copy only tracked fixture files; reject symlinks and special entries."""
    data = git(root, "archive", commit, "evals/app")
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive.getmembers():
            destination = contained(target, member.name)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.extractfile(member).read())
            else:
                raise ValueError("fixture archive contains a non-regular file")


def run_check(image, app, checks, test):
    name = "svh-" + uuid.uuid4().hex
    command = [
        "docker", "run", "--rm", "--name", name, "--pull=never",
        "--network=none", "--read-only", "--cap-drop=ALL",
        "--security-opt=no-new-privileges", "--pids-limit=64",
        "--memory=256m", "--cpus=1", "--ulimit", "nofile=256:256",
        "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=64m,mode=1777",
        "--mount", f"type=bind,src={app},dst=/app,readonly",
        "--mount", f"type=bind,src={checks},dst=/checks,readonly",
        image, test,
    ]
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if process.returncode:
            return {"status": "error", "docker_exit_code": process.returncode,
                    "stderr": process.stderr, "stdout": process.stdout}
        result = json.loads(process.stdout)
        result["status"] = classify(result)
        return result
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        return {"status": "error", "detail": str(error)}
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=15)


def verify(root, manifest_path, output, image="svh-eval:local"):
    manifest = json.loads(manifest_path.read_text())
    # Resolve the mutable local tag once; both sides must run the same image ID.
    image_id = subprocess.check_output(
        ["docker", "image", "inspect", image, "--format", "{{.Id}}"], text=True,
    ).strip()
    pre = git(root, "rev-parse", "--verify", manifest["pre_fix_commit"] + "^{commit}").decode().strip()
    post = git(root, "rev-parse", "--verify", manifest["post_fix_commit"] + "^{commit}").decode().strip()
    if pre == post:
        raise ValueError("pre-fix and post-fix commits must differ")
    results = []
    with tempfile.TemporaryDirectory(prefix="svh-") as directory:
        workspace = Path(directory)
        # Docker runs as nobody; parents must be traversable.
        workspace.chmod(0o755)
        checks = workspace / "checks"
        checks.mkdir()
        paths = ["conftest.py"] + [claim["test"] for claim in manifest["claims"]]
        hashes = {}
        for relative in paths:
            source = contained(root / "evals/reproductions", relative)
            destination = contained(checks, relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            data = source.read_bytes()
            destination.write_bytes(data)
            hashes[relative] = hashlib.sha256(data).hexdigest()
        for side, commit in [("pre", pre), ("post", post)]:
            app = workspace / side
            app.mkdir()
            snapshot(root, commit, app)
        for claim in manifest["claims"]:
            test = claim["test"]
            before = run_check(image_id, workspace / "pre", checks, test)
            after = run_check(image_id, workspace / "post", checks, test)
            results.append({
                "id": claim["id"], "test": test, "pre": before, "post": after,
                "verified": before["status"] == "assertion_failure" and after["status"] == "pass",
            })
    successes = sum(item["verified"] for item in results)
    report = {
        "kind": "fixture-oracle", "run_at": datetime.now(timezone.utc).isoformat(),
        "pre_fix_commit": pre, "post_fix_commit": post, "image_id": image_id,
        "test_sha256": hashes, "claims": results,
        "summary": {"verified": successes, "total": len(results),
                    "wilson_95": wilson(successes, len(results))},
        "m0_complete": False,
        "limitation": "Fixture tests only; owner recordings and 10–20 annotated bugs are still required.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report
