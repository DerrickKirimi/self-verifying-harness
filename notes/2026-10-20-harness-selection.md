# Harness selection before M1

[RUN] M0 is still running. No ingestion code or M1 dependencies were installed
for this investigation, and no paid model requests were made. Current package
metadata and dependency constraints are saved in
`notes/runs/m1-package-candidates.json` (checked 2026-10-20).

[CODE] Inspected the existing upstream clone
`/home/d3rrick/swe/llms/deepagents-upstream`, commit
`ade3f9560f45e3e6d018614e85a27b7c28841887`:

- `libs/deepagents/pyproject.toml`: version 0.7.26 and explicit Google model
  integration dependency. This clone is older than the package-index release.
- `libs/deepagents/deepagents/graph.py:277`: `create_deep_agent` accepts an
  explicit `BaseChatModel`, tools, middleware and backend. It owns the loop.
- `libs/deepagents/deepagents/backends/sandbox.py`: `BaseSandbox` derives
  filesystem operations from sandbox execution/file transfer. Concrete
  implementations provide execution and uploads. Do not use the owner's real
  filesystem or a local shell backend for generated code.

[SRC] [Current upstream documentation](https://github.com/langchain-ai/deepagents)
describes replaceable models/backends and MCP tools. Its documentation is not a
substitute for an installed-version smoke test. The new baseline is deepagents,
not a fork of the owner's older checkout and not a custom agent loop (D25).

[SRC] Official package-index metadata lists deepagents **0.7.28**,
langchain-google-genai **4.4.2**, MCP **2.3.0**, FastMCP **4.1.2**, and
langchain-mcp-adapters **0.3.2**. The last package explicitly requires
`mcp<2.0.0,>=1.24.0`. These are candidate versions and declared constraints,
not an installed or tested combination.

[SRC] [Official MCP v2 overview](https://py.sdk.modelcontextprotocol.io/whats-new/)
documents protocol 2026-07-28, the `MCPServer` rename, first-class `Client`,
request-scoped capabilities and multi-round-trip requests. It also explains
legacy-client compatibility. [Migration guide](https://py.sdk.modelcontextprotocol.io/migration/).

[INF] Use that official client/server pair and convert discovered MCP tool
schemas/results into the harness's tool objects. The conversion layer does not
own an agent loop or implement a parallel MCP protocol. This avoids an old SDK
constraint becoming an architectural limit. No need to adopt standalone
FastMCP merely because an earlier reference used it.

[INF] M1 integration checks must establish:

1. Actual pinned installed versions, negotiated protocol/capabilities, tools,
   resources, prompts and structured/image results over streamable HTTP.
2. Trusted paths, revisions and task handles stay server-owned. The model
   receives only permitted evidence and sandbox handles, never evaluation gold
   patches or owner credentials.
3. Every model call, including automatic summarization or other middleware,
   goes through the persistent cost guard. Disable model/provider retries and
   delegation for the baseline; no unrelated paid tools or implicit model.
4. Reads, edits and generated code execution stay in restricted Docker.
   Verifier logs and held-out tests remain outside the writable agent sandbox.
5. Relevant modern capabilities are exercised, and unsupported extensions or
   legacy fallbacks are recorded explicitly. A documentation read is not an
   interoperability result.

[INF] Claude Code and other MCP clients remain possible integrations; they are
not needed to spend an unauthorized model account or to unblock the first
Gemini-backed demonstration. Retrieval model/store choices still depend on M0
measurements; selecting the harness does not select an embedder or database.
