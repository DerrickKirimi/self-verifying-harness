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
