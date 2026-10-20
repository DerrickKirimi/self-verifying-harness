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

## Decisions (20 Oct 2026, public datasets and execution backends)

| # | Decision | Why / evidence |
|---|---|---|
| D17 | **Docker now; interchangeable execution backends later as needed.** Supersedes the SPACE-specific evaluation commitment in D7. | Owner explicitly named E2B and Daytona as future options. [SRC] Keep task identity, immutable source/test inputs and evidence reports independent of the backend. The current runner invokes Docker directly; an Executor interface and cloud implementations are not yet built. [CODE/INF] |
| D18 | **Owner narration is not a prerequisite for the visual verification path.** M0 can use vetted public video/task pairs alongside controlled local fixtures. | The project accepts claims spoken **or shown**. [SRC] The public-dataset audit found concrete video + code + test candidates. Public cases require provenance, reuse permission, privacy screening and our own failing/passing runs before acceptance. Speech/STT performance must be measured separately on appropriate audio. [INF] |

Evidence and candidate revisions: `notes/2026-10-20-public-dataset-audit.md`.
No public candidate is verified or included in M0 yet. [RUN]

## Decisions (20 Oct 2026, primary benchmark pilot)

| # | Decision | Why / evidence |
|---|---|---|
| D19 | **Use the pinned current SWE-bench Multimodal release as the primary visual-task source; supplement its media coverage as needed.** Supersedes the next-step priority for CodeV in the first audit. | Owner delegated selection and expressed interest in this benchmark. [SRC] Actual Parquet inspection found direct video and GIF candidates, and the official site documents a recent v2 environment/grading refresh. [RUN/SRC] Newer-model difficulty and media contribution remain unmeasured. [INF] |
| D20 | **Keep one implementation branch and isolated adapters/artifacts.** | No conflicting product implementations yet justify branch divergence. [INF] Start with the native BPMN color-label oracle; keep raw data and gold patches ignored, then attach annotated media after the oracle succeeds. |

## Decisions (20 Oct 2026, external corpus admission)

| # | Decision | Why / evidence |
|---|---|---|
| D21 | **Represent external source states as an immutable base commit plus hashed source/test patches and a pinned Docker image.** | The benchmark supplies patches, not a second Git commit. The external schema binds these bytes, the pinned dataset row, decoded media and frozen execution logs. It does not invent a post-fix commit. [CODE] |
| D22 | **M0 admission requires 10–20 distinct reviewed temporal artifacts, every supplied oracle passing, and a 95% Wilson lower bound of at least 0.70.** | This numerical threshold was set before measuring the full corpus; it supplements the requirement that every admitted reproduction fail by assertion before and pass after. Curated admission is not model success or independent sampling. Rejected candidates remain recorded separately. [INF/CODE] |
| D23 | **Use a conservative local API budget with per-request cost reservations before paid requests.** | The owner authorized shared Gemini credentials and supplied prepaid balance/cap evidence. Provider billing limits have enforcement latency; the local ledger must retain reservations after ambiguous failures and disable implicit retries. Secret files, screenshots and account identifiers remain outside commits. [SRC/INF] |
| D24 | **Review oracle-to-claim alignment explicitly before corpus admission. A passing test for a supporting invariant does not verify the broader recorded symptom.** | Case 1578 was initially admitted after its native oracle passed, then excluded when code review showed its sole failing test checks subprocess diagram-object identity rather than the recorded pool-copy/export/ID behavior. The historical proof remains, and the annotation is archived under `evals/excluded/`. Each review now records the exact exercised behavior and alignment judgment. [CODE/INF] |
| D25 | **Select deepagents as the first executable agent harness and the official MCP v2 client/server for M1, with a thin tool bridge rather than the current LangChain MCP adapter.** Supersedes the provisional Claude Code choice in D13. | The authorized model access is Gemini; deepagents accepts an explicit chat model and sandbox backend without forking its loop. [CODE/SRC] Current PyPI metadata lists deepagents 0.7.28 and MCP 2.3.0, but langchain-mcp-adapters 0.3.2 requires `mcp<2.0.0`. The official v2 SDK speaks protocol 2026-07-28. [SRC] Installation, transport interoperability, disabled delegation/retries, Docker isolation and budget coverage must be demonstrated at M1 before calling the integration working. [INF] |
| D26 | **Fix the remaining MVP acceptance protocol before model measurements.** | `evals/PROTOCOL.md` specifies M1 retrieval comparisons and confidence thresholds, M2 claim precision/recall and grounding, M3 generated-check and actual repair evidence, wrong-fix controls and executed Harbor nop/oracle trials. These are prospective engineering criteria, not population-quality claims. Silent visual admission cannot establish speech quality. [INF] |
