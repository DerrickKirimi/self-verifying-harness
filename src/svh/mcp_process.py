"""Managed loopback evidence server; its process receives no model credentials."""
import asyncio
from contextlib import asynccontextmanager
import os
import socket
import subprocess
import sys

import httpx2
from svh.mcp_server import private_token
from svh.mcp_client import connect


@asynccontextmanager
async def evidence_client(root, corpus, log_path, *, task_manifest=None):
    token_file = root / "data/runtime/mcp.token"
    token = private_token(token_file)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}/mcp"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w") as log:
        process = subprocess.Popen([sys.executable, "-I", "-m", "svh.cli", "--root", str(root),
            "mcp", *( ["--task-manifest", str(task_manifest)] if task_manifest is not None else ["--corpus", str(corpus)] ), "--port", str(port)], cwd=root,
            env={"PATH": os.environ["PATH"], "LANG": "C.UTF-8", "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"},
            stdout=log, stderr=subprocess.STDOUT)
        try:
            async with asyncio.timeout(150):
                async with httpx2.AsyncClient() as http:
                    while True:
                        if process.poll() is not None:
                            raise ValueError("Evidence server failed to start; inspect its local log")
                        try:
                            if (await http.get(url, timeout=2)).status_code == 401:
                                break
                        except (httpx2.ConnectError, httpx2.TimeoutException):
                            pass
                        await asyncio.sleep(.2)
            async with connect(url, token) as client:
                yield client
        finally:
            process.terminate()
            try:
                await asyncio.to_thread(process.wait, timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                await asyncio.to_thread(process.wait, timeout=10)
