# M1 checkpoint: real MCP HTTP evidence boundary

[RUN] Installed the locked optional `agent` stack after M0 passed: MCP 2.3.0,
deepagents 0.7.28, langchain-google-genai 4.4.2 and google-genai 2.31.0.
Exact imports/signatures: `notes/runs/m1-installed-preflight.json`.

[CODE] `svh mcp` binds only to loopback and serves registered recording metadata,
bounded timestamped PNG frames, silent-media transcript status, two resources
and `inspect_recording_v1`. Paths, source selection and the frozen corpus stay
server-owned; tool schemas expose recording identifiers and time bounds. The
evidence store deliberately omits gold claims, patches, test names and grader
paths. `get_transcript` raises for audio that has not been transcribed; this is
not an implemented speech ingestion path or an M1 completion claim.

[CODE/RUN] Owner-only local bearer tokens are generated under ignored
`data/runtime/`. Real HTTP tests reject missing authorization, foreign web origins,
unknown/traversal-like IDs, invalid frame intervals/counts and changed media.
Tool metadata declares read-only/idempotent operations. The server accepts no
generated code and makes no model requests.

[RUN] Actual MCP SDK HTTP test negotiated **2026-07-28**, exercised tools,
resources and the versioned prompt, checked structured results and PNG blocks,
and preserved images through a thin LangChain tool bridge. It also invoked the
existing deepagents loop with a deterministic test model, which called the MCP
metadata tool and received its structured artifact. External tracing is disabled
in that test. This verifies integration plumbing, not model judgment or an
agent-generated reproduction. Full suite: **57 passed**.

[RUN] `scripts/smoke_mcp_http.py` separately launched the actual CLI using the
frozen eleven-case public corpus. Its child inherited no model credentials.
The real pilot video returned PNG frames at **5.45 s and 6.35 s** and explicit
`no_audio` status. Corpus identity matched, unauthorized HTTP returned 401, and
the server was terminated afterward. Public report:
`notes/runs/mcp-http-smoke.json`. No paid model calls were made.

[INF] No legacy protocol fallback was needed. Tasks/Apps/Skills extensions,
sampling and elicitation are not advertised or claimed by this checkpoint.
The SDK is current; only the capabilities exercised above are demonstrated.

## Run

```sh
uv sync --locked --extra datasets --extra agent
uv run --all-extras svh mcp --port 8765
# In another terminal, run the credential-free smoke test and its own server:
uv run --all-extras python -I scripts/smoke_mcp_http.py
```

[CODE] `svh.mcp_client.connect` loads an explicitly supplied local token into an
HTTP header; it never embeds it in a URL. The token file is owner-readable only,
and no token/API key appears in public reports. No Kubrick or Pixeltable runtime
dependency was adopted; the bridge uses the official MCP client rather than the
released LangChain adapter's older SDK constraint.

[INF] Next required work: model transport reservations covering retries and all
middleware paths; actual ingestion, transcript/OCR and retrieval; M1 measurement
against the frozen corpus and baseline. M2/M3 and Harbor remain unmeasured.
