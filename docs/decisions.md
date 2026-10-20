# Decisions and open questions

Append new decisions; don't rewrite old ones. To reverse a decision, add a new entry that supersedes it.

## Decisions (17 Oct 2026, bootstrap)

| # | Decision | Why |
|---|---|---|
| D1 | **The product's core is claims → verified checks; the meeting bot is one input channel.** | The original idea has no oracle (`analysis.md` §3). Verification is what makes the output trustworthy, and it doubles as an RL-task generator. |
| D2 | **A reproduction counts only if it was observed failing before the fix and passing after.** | The integrity rule; it mirrors Harbor's oracle/nop check. |
| D3 | **Eval set (M0) before any feature code.** | No gate can be measured without it. Kubrick and the OCR course both shipped without one. |
| D4 | **Offline recordings first; live meetings at M5; telephony at M6.** | Each live channel adds hard dependencies and nothing to verify. |
| D5 | **MCP (FastMCP, streamable HTTP) is the boundary; the owner's existing harness is the client.** | Reuses Claude Code, deepagents and others; avoids building an agent loop. |
| D6 | **Python + `uv`.** | Kubrick, Pixeltable, FastMCP, Playwright and the embedding stack are all Python. |
| D7 | **Docker for the M0–M3 sandbox, behind an `Executor` interface; SPACE evaluated at M4.** | SPACE needs KVM + btrfs + Kind and its installer assumes apt; the laptop runs Manjaro. Don't block the MVP on it. |
| D8 | **Scion is not adopted for the MVP; evaluated at M5 for roles and chat channels.** | A single pipeline doesn't need multi-agent orchestration yet. |
| D9 | **EmbeddingGemma 2 is a retrieval column, not the "ear".** | Model card: video Hit@1 50.67. Transcript and timestamp search stay primary. |
| D10 | **Voice is never sufficient authorization for a write action.** | Voice cloning. A second factor is required. |

## Open questions for the owner

1. **The M0 app.** Which small web app will you build or reuse for the eval set? It needs bugs worth filming. Planting them, as SWE-smith does, is fine.
2. **The STT path for M1.** An API (fast to start) or `faster-whisper` + `pyannote` locally (learn self-hosting)? Check current model names and prices first.
3. **The health/FHIR track** (Nova 2 Sonic, DHA eClaims): a second track after M3, or parked?
4. **Meeting bot at M5.** Is a hosted meeting-bot API acceptable, or is self-hosting the join step part of what you want to learn?
5. **"Anthropic's Sion".** Please add a link to `docs/references.md` so it can be compared with Scion from a primary source.
6. **The GitHub repo is public.** The idea files contain your own dictated thoughts, and the docs name local paths and your other projects. The bootstrap commit wasn't pushed for that reason. Push once you're happy for all of it to be public.

## Decisions (20 Oct 2026, first implementation)

| # | Decision | Why / evidence |
|---|---|---|
| D11 | **References are replaceable evidence, never inherited architecture.** Supersedes the Kubrick-specific part of D5. MCP remains the intended integration boundary; the Python SDK/server framework is selected at M1. | Owner's explicit direction in this session. [SRC] No Pixeltable or reference-project dependency is included in the M0 implementation. [CODE] |
| D12 | **Use the repo's own small issue board for the first three M0 fixtures.** | Fictional local data, deterministic HTTP behaviour, no credentials or existing product needed. [CODE] This is an implementation choice pending any owner preference for a different app. [INF] |
| D13 | **First client baseline: Claude Code through standard MCP, without forking its loop.** Client selection is provisional pending the owner's answer; the verifier stays a standalone Python library/CLI. | Claude Code documents HTTP MCP configuration and server prompts. [SRC] This establishes integration feasibility, not a comparative quality result. No client integration or agent-driven fixes have been measured yet. |
| D14 | **M0 fixture oracle first; no ingestion code before the M0 gate.** | Three hand-written HTTP checks use one frozen test snapshot against two archived Git revisions, in Docker. Setup/collection errors, skips and empty runs do not verify a claim. [CODE] These fixtures are not narrated walkthroughs and do not pass M0. |
| D15 | **Select retrieval on measured M0 results, not the age or sophistication of a reference.** | No retrieval store, OCR stack, embedder integration or STT provider is selected by this session. [CODE] An embedding model and a complete ingestion/retrieval system are separate decisions; whether any model meets our needs remains unmeasured. [INF] |
| D16 | **Implement current MCP capabilities supported by both sides, with explicit fallbacks.** | On 2026-10-20, the specification's `latest` URL resolves to `2026-07-28`; it documents per-request capability negotiation, core resources/prompts/tools and elicitation, and opt-in Tasks, Skills and Apps extensions. [SRC] At M1, check SDK and client support before pinning dependencies; evaluate Tasks for long verification runs and Apps for evidence review. No support is claimed from reading the specification alone. |

Sources for D13/D16: [Claude Code MCP](https://code.claude.com/docs/en/mcp),
[MCP specification](https://modelcontextprotocol.io/specification/2026-07-28), read 2026-10-20.
The owner's written instruction to implement and ship, together with the supplied
AGENTS.md commit/push instruction, authorizes the repository pushes for this work. [SRC]
