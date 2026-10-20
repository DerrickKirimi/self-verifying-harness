"""Actual isolation/transfer/cleanup checks with a public immutable buggy image."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

from svh.docker_backend import sandbox
from svh.native import IMAGE

root = Path(__file__).resolve().parents[1]
base = "7478388070d83e8802c873e8480dbf23ae3ace3a"
os.environ["SVH_TEST_HOST_SECRET"] = "controlled-marker-never-forward"
with tempfile.NamedTemporaryFile(prefix="svh-host-private-") as marker:
    with sandbox(IMAGE, base) as backend:
        name = backend.id
        source_archive_sha256 = backend.source_archive_sha256
        initial_source_fingerprint = backend.initial_source_fingerprint
        inspect = json.loads(subprocess.check_output(["docker", "inspect", name]))[0]
        config = inspect["HostConfig"]
        assert config["NetworkMode"] == "none" and config["ReadonlyRootfs"]
        assert config["Memory"] == 4 * 1024 ** 3 and config["NanoCpus"] == 2_000_000_000
        assert not [mount for mount in inspect["Mounts"] if mount["Type"] == "bind"]
        assert "ALL" in config["CapDrop"] and "no-new-privileges" in config["SecurityOpt"]
        checks = {
            "fresh_history": "test $(git rev-list --count HEAD) = 1 && test -z \"$(git remote)\" && test -z \"$(ls -A /testbed/.git)\"",
            "host_file_hidden": "test ! -e " + shlex.quote(marker.name),
            "host_environment_hidden": "test -z \"${SVH_TEST_HOST_SECRET:-}\" && test -z \"${GEMINI_API_KEY:-}\" && test -z \"${GOOGLE_API_KEY:-}\"",
            "root_read_only": "if touch /root/svh-forbidden 2>/dev/null; then exit 1; fi",
            "working_directory": "test \"$(pwd)\" = /workspace",
            "network_unreachable": "python3 -I -c " + shlex.quote("import socket\ntry: socket.create_connection(('1.1.1.1',443),.5)\nexcept OSError: pass\nelse: raise SystemExit(1)"),
        }
        results = {label: backend.execute(command).exit_code == 0 for label, command in checks.items()}
        assert all(results.values()), results
        source_read = backend.read("/workspace/package.json", offset=0, limit=5)
        assert source_read.error is None and source_read.file_data
        assert "bpmn-js" in str(source_read.file_data["content"])
        results["sdk_source_read_helper"] = True
        matches = backend.glob("**/*SetColorHandler*")
        assert matches.error is None and matches.matches
        assert all(item["path"].startswith("/workspace/") for item in matches.matches)
        results["default_glob_scoped_to_project"] = True
        content = b"literal data: $(touch /root/never) `not shell`\n"
        assert backend.upload_files([("/workspace/controlled.txt", content)])[0].error is None
        assert backend.download_files(["/workspace/controlled.txt"])[0].content == content
        assert backend.source_fingerprint() != initial_source_fingerprint
        assert backend.upload_files([("/root/forbidden", b"no")])[0].error == "invalid_path"
        assert backend.execute("python3 -I -c 'print(\"x\"*100000)'").truncated
        results["file_roundtrip_and_output_bound"] = True
        timeout = backend.execute("sleep 3", timeout=1)
        assert timeout.exit_code is None and backend.closed
        results["timeout_destroys_execution_domain"] = True
    remaining = subprocess.run(["docker", "inspect", name], capture_output=True)
    assert remaining.returncode != 0
report = {"passed": True, "image": IMAGE, "base_commit": base,
          "source_archive_sha256": source_archive_sha256,
          "initial_source_fingerprint": initial_source_fingerprint,
          "checks": results, "cleanup": "container absent", "generated_code_executed_on_host": False}
(root / "notes/runs/docker-backend-smoke.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
