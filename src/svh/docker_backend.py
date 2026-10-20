"""Deepagents backend: generated commands run only in an isolated container.

The image root is read-only; writable files live in bounded tmpfs mounts.
No owner paths, environment credentials, Docker socket or network are exposed.
"""
import base64
import hashlib
from contextlib import contextmanager
import json
import os
import re
import selectors
import subprocess
import time
import uuid

from deepagents.backends.sandbox import BaseSandbox
from deepagents.backends.protocol import ExecuteResponse, FileUploadResponse, FileDownloadResponse


class DockerSandbox(BaseSandbox):
    def __init__(self, image, base_commit):
        if (not re.fullmatch(r"(?:[A-Za-z0-9_./:-]+@)?sha256:[0-9a-f]{64}", image)
                or not re.fullmatch(r"[0-9a-f]{40}", base_commit)):
            raise ValueError("A trusted immutable image and base commit are required")
        self.image, self.base_commit = image, base_commit
        self.name = "svh-agent-" + uuid.uuid4().hex
        self.closed = True

    @property
    def id(self):
        return self.name

    def start(self):
        archive = subprocess.run(["docker", "run", "--rm", "--pull=never", "--network=none",
            "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges", "--log-driver=none",
            "--entrypoint", "git", self.image, "-C", "/testbed", "archive", "--format=tar", self.base_commit],
            capture_output=True, timeout=60, check=True).stdout
        if len(archive) > 32 * 1024 ** 2:
            raise ValueError("Source archive exceeds sandbox staging limit")
        self.source_archive_sha256 = hashlib.sha256(archive).hexdigest()
        command = ["docker", "run", "--detach", "--name", self.name, "--pull=never", "--init",
            "--network=none", "--read-only", "--cap-drop=ALL", "--cap-add=SETUID", "--cap-add=SETGID",
            "--security-opt=no-new-privileges", "--memory=4g", "--cpus=2", "--pids-limit=512",
            "--shm-size=512m", "--log-driver=none",
            "--tmpfs", "/workspace:rw,nosuid,size=1536m",
            "--tmpfs", "/tmp:rw,nosuid,size=512m",
            "--tmpfs", "/testbed/.git:rw,noexec,nosuid,size=1m",
            "--tmpfs", "/testbed/node_modules/.cache:rw,nosuid,size=256m",
            "--workdir", "/workspace", "--entrypoint", "/bin/sleep", self.image, "infinity"]
        try:
            subprocess.run(command, capture_output=True, check=True, timeout=30)
            self.closed = False
            subprocess.run(["docker", "exec", "-i", self.name, "tar", "-xf", "-", "-C", "/workspace"],
                           input=archive, capture_output=True, check=True, timeout=30)
            result = self.execute("ln -s /testbed/node_modules /workspace/node_modules && "
                "git init -q /workspace && git -C /workspace add -A && "
                "git -C /workspace -c user.name=svh -c user.email=sandbox@localhost commit -qm baseline", timeout=30)
            if result.exit_code != 0:
                raise ValueError("Could not initialize the history-stripped source checkout")
            self.initial_source_fingerprint = self.source_fingerprint()
            return self
        except BaseException:
            self.close()
            raise

    def close(self):
        subprocess.run(["docker", "rm", "-f", self.name], capture_output=True, timeout=20)
        self.closed = True

    def execute(self, command, *, timeout=None):
        if self.closed:
            raise ValueError("Sandbox is not running")
        if not isinstance(command, str) or not 0 < len(command) <= 100_000:
            raise ValueError("Supply a bounded shell command")
        duration = min(300, timeout if timeout is not None else 120)
        if duration <= 0:
            raise ValueError("Execution timeout must be positive")
        process = subprocess.Popen(["docker", "exec", "--workdir", "/workspace", self.name,
            "timeout", "--kill-after=5s", str(duration), "/bin/bash", "-lc", command],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, truncated = bytearray(), False
        deadline = time.monotonic() + duration + 10
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                while selector.get_map():
                    if time.monotonic() >= deadline:
                        self.close()  # Kill the whole execution domain, including children.
                        process.kill()
                        return ExecuteResponse(output=output.decode(errors="replace") + "\nSandbox execution timed out.", exit_code=None, truncated=truncated)
                    for key, _ in selector.select(timeout=.2):
                        block = os.read(key.fileobj.fileno(), 8192)
                        if not block:
                            selector.unregister(key.fileobj)
                            continue
                        available = max(0, 65_536 - len(output))
                        output.extend(block[:available])
                        truncated |= len(block) > available
            code = process.wait(timeout=10)
            # An inner timeout is infrastructure, never an assertion failure.
            if code in (124, 137):
                self.close()
                code = None
            return ExecuteResponse(output=output.decode(errors="replace"), exit_code=code, truncated=truncated)
        finally:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
            process.stdout.close()

    def _files(self, operation, items):
        if self.closed or len(items) > 32:
            raise ValueError("Sandbox unavailable or file batch too large")
        # Paths and content are JSON on stdin, never interpolated into host code.
        script = r'''
import base64,json,pathlib,sys
operation,items=json.load(sys.stdin)
results=[]
for item in items:
    raw=item[0] if operation=='upload' else item
    path=pathlib.Path(raw)
    row={'path':raw}
    try:
        resolved=path.resolve()
        if not path.is_absolute() or not any(resolved.is_relative_to(root) for root in (pathlib.Path('/workspace'),pathlib.Path('/tmp'))):
            row['error']='invalid_path'
        elif operation=='upload':
            content=base64.b64decode(item[1],validate=True)
            if len(content)>4*1024**2: raise ValueError()
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(content)
        else:
            with path.open('rb') as stream: content=stream.read(4*1024**2+1)
            if len(content)>4*1024**2: raise ValueError()
            row['content']=base64.b64encode(content).decode()
    except FileNotFoundError: row['error']='file_not_found'
    except IsADirectoryError: row['error']='is_directory'
    except (PermissionError,OSError): row['error']='permission_denied'
    except ValueError: row['error']='file_size_or_encoding'
    results.append(row)
print(json.dumps(results))
'''
        result = subprocess.run(["docker", "exec", "-i", self.name, "python3", "-I", "-c", script],
            input=json.dumps([operation, items]).encode(), capture_output=True, check=True, timeout=30)
        return json.loads(result.stdout)

    def source_fingerprint(self):
        """Hash actual workspace bytes, independent of model-editable git state."""
        import shlex
        script = r'''
import hashlib,os,pathlib
root=pathlib.Path('/workspace'); digest=hashlib.sha256()
for directory,dirs,files in os.walk(root,followlinks=False):
    dirs[:]=sorted(name for name in dirs if name not in ('.git','node_modules'))
    for name in sorted(files):
        path=pathlib.Path(directory)/name
        digest.update(str(path.relative_to(root)).encode()+b'\0')
        if path.is_symlink(): digest.update(b'link:'+os.readlink(path).encode())
        else:
            file_hash=hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(65536),b''): file_hash.update(block)
            digest.update(file_hash.digest())
        digest.update(b'\0')
print(digest.hexdigest())
'''
        result = self.execute("python3 -I -c " + shlex.quote(script), timeout=30)
        value = result.output.strip()
        if result.exit_code != 0 or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("Could not fingerprint sandbox source")
        return value

    def upload_files(self, files):
        if sum(len(data) for _, data in files) > 8 * 1024 ** 2:
            raise ValueError("Upload batch exceeds eight MiB")
        rows = self._files("upload", [(path, base64.b64encode(data).decode()) for path, data in files])
        return [FileUploadResponse(path=row["path"], error=row.get("error")) for row in rows]

    def download_files(self, paths):
        rows = self._files("download", paths)
        return [FileDownloadResponse(path=row["path"], error=row.get("error"),
                                    content=base64.b64decode(row["content"]) if "content" in row else None) for row in rows]


@contextmanager
def sandbox(image, base_commit):
    backend = DockerSandbox(image, base_commit)
    try:
        yield backend.start()
    finally:
        backend.close()
