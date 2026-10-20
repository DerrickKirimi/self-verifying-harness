# References

Local clones live in `~/swe/llms/<repo>`. Commits are as read on the date shown. "Read" means read for this project; anything else is listed as not read.

## Code read

| Source | Local | Commit / date | What it gives this project |
|---|---|---|---|
| Kubrick: `the-ai-merge/multimodal-agents-course` | `~/swe/llms/multimodal-agents-course` | `8dc13da`, 2026-01-06 | MCP server with tools + resources + versioned prompts; Pixeltable multimodal ingestion; server-side argument injection; Opik traces with media. Bugs to avoid: `analysis.md` §6 |
| Production OCR course: `neural-maze/production-ocr-course` | `~/swe/llms/production-ocr-course` | `4d147f0`, 2026-09-01 | Layout-then-VLM OCR; producer/queue/worker; vLLM serving flags; KEDA on `vllm:num_requests_waiting`; an MCP submit-and-poll wrapper |
| SPACE: `perplexityai/SPACE` | `~/swe/llms/SPACE` | `253d8b34`, 2026-10-15 (first commit 2026-10-05) | Firecracker microVM sandboxes over HTTP/SSE; templates, suspend snapshots, egress policy, credential injection; E2B-compatible wrapper. Read: README, `docs/architecture.md`, `docs/installation.md` (prerequisites), `docs/introduction.md` |
| Scion: `GoogleCloudPlatform/scion` (fork `DerrickKirimi/scion`) | `~/swe/llms/scion` | `3fc3b040e`, 2026-10-17 (nightly-20261017; latest preview tag `v0.3.0-preview.3`) | Multi-agent orchestration of harness agents in containers; Hub; messaging and chat gateways; A2A bridge; harness bundles. Read: README, `docs-site/.../philosophy.md`, `supported-harnesses.md` (intro) |
| Temporal + Composio + KEDA: `shricodev/kron-k8s-agent` | `~/swe/llms/kron-k8s-agent` | `1eb10f1`, 2026-06-23 | A durable agent workflow, and why one activity per whole loop is wrong for side effects |
| LangGraph + MCP + A2A book: `sandeepmb/freecodecamp-multi-agent-ai-system` | `~/swe/llms/freecodecamp-multi-agent-ai-system` | `6b3b01c`, 2026-04-25 | Checkpoint + `interrupt()` + `update_state(as_node=)` for human approval steps; two-tier tests with calibrated LLM judges |

## Models

- **EmbeddingGemma 2**, `google/embeddinggemma-2` on the Hugging Face Hub (updated 2026-10-06). Specs and benchmarks are in `analysis.md` §5.

## Study docs (owner's library, `~/Desktop/CLAUDE-DOCS/study-series/md/`)

- `practical_projects_map.md`: the analysis this repo started from (§8 Kubrick, §7 OCR course, §9 the idea, §12 the integration plan).
- `harness_stack_deep_dive.md`: the Harbor task format (§4–5), oracle/nop (§14.2), eval statistics with Wilson and MDE (§10.4), tracing via `harbor-atif2otel` (§14.1).

## Supplied in the original idea, not yet read

- AWS, *Build a healthcare appointment agent with Amazon Nova 2 Sonic*: https://aws.amazon.com/blogs/machine-learning/build-a-healthcare-appointment-agent-with-amazon-nova-2-sonic/
- Kenya DHA FHIR eClaims use cases: https://fhir.dha.go.ke/ig/eclaims/usecases.html
- LiveKit SIP primer: https://docs.livekit.io/reference/telephony/sip-primer/
- Kubrick course round-up: https://read.theaimerge.com/p/kubrick-course-final-round-up
- EmbeddingGemma 2 developer guide: https://developers.googleblog.com/embeddinggemma-2-the-developer-guide/

## To add

- Anthropic's "Sion" (named by the owner; no source on disk yet).

## Current integration sources (read 2026-10-20)

- [MCP specification, current latest](https://modelcontextprotocol.io/specification/2026-07-28).
  The `latest` URL redirected to this revision. Read the overview: core features,
  per-request capability negotiation, utilities and opt-in extensions. [SRC]
  SDK/client implementation support has not yet been checked; selecting it is M1 work.
- [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp).
  Read HTTP transport configuration and project/client integration sections. [SRC]
  Used only to establish the provisional first client's MCP integration path,
  not to claim comparative harness quality or successful local integration.
