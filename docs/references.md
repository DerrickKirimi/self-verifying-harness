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

### Harness preflight (read 2026-10-20)

- [deepagents upstream](https://github.com/langchain-ai/deepagents) and
  [backend documentation](https://docs.langchain.com/oss/python/deepagents/backends).
  Local upstream clone `/home/d3rrick/swe/llms/deepagents-upstream`, commit
  `ade3f9560f45e3e6d018614e85a27b7c28841887`: read explicit model/middleware/backend
  parameters and base sandbox implementation. That clone is version 0.7.26;
  current package metadata lists 0.7.28. [CODE/SRC]
- [Official MCP SDK](https://github.com/modelcontextprotocol/python-sdk),
  [v2 overview](https://py.sdk.modelcontextprotocol.io/whats-new/) and
  [migration guide](https://py.sdk.modelcontextprotocol.io/migration/).
  Read high-level client/server and protocol change sections; no SDK installed
  or interoperability result produced yet. [SRC/RUN]
- [LangChain MCP adapters](https://github.com/langchain-ai/langchain-mcp-adapters).
  Read repository overview and official package metadata; released adapter 0.3.2
  requires MCP <2, so it is not the selected bridge (D25). [SRC/INF]
- Official PyPI JSON metadata for `deepagents`, `mcp`, `fastmcp`,
  `langchain-mcp-adapters` and `langchain-google-genai`: version, release time,
  Python requirements and dependency constraints recorded with exact URLs in
  `notes/runs/m1-package-candidates.json`. Selection rationale and unmeasured
  integration checks: `notes/2026-10-20-harness-selection.md`. [RUN/INF]

## Public evaluation candidates (read 2026-10-20)

No external candidate has passed our oracle yet. [RUN] Detailed inspection scope
and local temporary download locations are in
`notes/2026-10-20-public-dataset-audit.md`.

| Source | Revision / inspection | Potential use |
|---|---|---|
| [E2E Tests Dataset](https://github.com/e2e-tests-dataset/e2e-tests-dataset), [paper](https://doi.org/10.1007/s11219-021-09566-x) | `cfc3aa4641ee2083a5bd9309e7ba860966e9771b`; repository tree, selected case README, Docker README, submodules, one video metadata | Browser recordings linked to bug/fix tags and e2e tests; legacy runtime and reuse permission unverified. [SRC/CODE] |
| [CodeV / Visual SWE-bench](https://github.com/luolin101/CodeV) | `46a6b65bf57f24cd33eddbc2445583939207df37`; README, tree and video-only JSON | One video task with base revision, fix/test patches and test identifiers; execution and reuse permission unverified. [CODE/RUN] |
| [SWE-bench Multimodal](https://huggingface.co/datasets/SWE-bench/SWE-bench_Multimodal/blob/main/README.md) | README last-listed revision `4e6662d51c48e475f7f346e4fa09a6f8b31fcaa5`; card and file listing, not task rows | Filter mixed visual assets for video-bearing tasks with runnable oracles. [SRC/INF] |
| [TANGO](https://two-to-tango.github.io/tango/) | Overview read; no archive downloaded | Bug videos for duplicate detection; repair oracle not established by the overview. [SRC] |

## SWE-bench Multimodal native pilot (2026-10-20)

- [SRC] [Official v2 update](https://www.swebench.com/multimodal.html), dated
  2026-09-01; environment/grading refresh and 480 selected test tasks.
- [CODE] Official harness reference clone: `/home/d3rrick/swe/llms/SWE-bench`,
  `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`. Read native eval-script execution,
  image-asset staging, BPMN log parser, grading and TestSpec. Its full package
  is not a product dependency; the pilot consumes the released task contract.
- [RUN] Read both Parquet files at dataset revision
  `4e6662d51c48e475f7f346e4fa09a6f8b31fcaa5`, verified file hashes and audited all
  580 rows. Exact inventory: `notes/runs/swebench-multimodal-audit.json`.
- [RUN] BPMN native oracle pilot passed; report and raw-log hashes in
  `notes/runs/swebench-bpmn-pilot.json`. Scope, commands and limitations:
  `notes/2026-10-20-swebench-multimodal-pilot.md`.

## Literature review sources (read 2026-10-20)

Ordered discussion and implications: [literature-review.md](literature-review.md).
These are primary papers or author repositories/project pages. [SRC] Inspection
was section-scoped, not a cover-to-cover review or reproduction of external
results. [RUN] No external system was executed for this review. Paper links pin
the inspected version where available; mutable web repositories are not pinned
dependencies. No local clones were created for these readings. [RUN]

| Source | Version / scope read | Relevance |
|---|---|---|
| [GUIRepair: Seeing is Fixing](https://arxiv.org/html/2506.16136v1), [author project](https://sites.google.com/view/guirepair) | v1 (2025); motivation, §III, evaluation setup, project reproduction instructions | Visual report → repro code → rendered patch feedback |
| [ViBR](https://arxiv.org/html/2604.19905v1) | v1 (2026); §2, §3.3, threats/data availability | Recording-driven Android bug replay |
| [Beyond Fail-to-Pass / CoHarden](https://arxiv.org/html/2607.19843v1) | v1 (2026); §2–3, discussion/implementation notes | Lax assertions, test/fix coupling, mutation challenges |
| [VisualRepair](https://arxiv.org/html/2607.14075v1) | v1 (2026); §III–IV, parameter studies | Direct Multimodal successor; GIFs, crops, patch selection |
| [FailureMem](https://arxiv.org/html/2603.17826v1) | v1 (2026); §3, setup, appendix A and visual tools | Direct Multimodal successor; failure memories and gold separation |
| [SWE-bench Multimodal paper](https://arxiv.org/html/2410.03859v1) | v1 (2024); §2–4; current release page already listed above | Dataset/oracle construction; SWE-agent M browser tools |
| [OpenHands-Versa paper](https://arxiv.org/html/2506.03011v1), [repo](https://github.com/adityasoni9998/OpenHands-Versa) | v1 (2025); tools, protocol, analysis/failures; mutable README | Existing coding harness with visual browsing; Multimodal evaluation |
| [Framesleuth](https://github.com/thestackhub1/framesleuth-agent) | Mutable README: architecture, bundles, grounding, quality/eval descriptions; code not audited | Recording-to-MCP product overlap |
| [Agentless Lite](https://github.com/sorendunn/Agentless-Lite) | Mutable README: method/retrieval/artifacts; code not audited | Minimal direct Multimodal repair baseline |
| [CodeV](https://github.com/luolin101/CodeV) | README workflow; prior pinned dataset audit listed above | Visual-to-text pipeline baseline |
| [SWT-Bench paper](https://arxiv.org/abs/2406.12952), [harness](https://github.com/logic-star-ai/swt-bench) | Early v1 HTML formulation/metrics/method (title differs from final paper); current README | Generated-test evaluation before/after gold fix |
| [ReProAgent](https://arxiv.org/html/2607.09123v1) | v1 (2026); task formulation, stages/tools, semantic failure review | Reproduction planning and failure attribution |
| [ReBug](https://arxiv.org/html/2608.03598v1) | v1 (2026); §III–IV | Browser prerequisites and procedure-execution evaluation |
| [SWEeper-Bench](https://sweeperbench.com/) | Project page: protocol, verifier calibration, worked example; paper/code not audited | Browser discovery, target/preservation procedures |
| [Replay Web Debug Bench](https://www.replay.io/blog/web-debug-bench) | Author announcement dated 2026-04-07; protocol/generation/scoring/example | Instrumented browser recordings for diagnosis |
| [V2S+](https://arxiv.org/html/2301.01191v1) | v1 (2023); introduction, input requirements, detection/replay design | Touch-indicator-based replay precedent |
| [GIFdroid](https://arxiv.org/html/2112.04128v1) | v1 (2021); introduction and approach | Keyframe-to-UI-graph replay precedent |
| [CAPdroid](https://arxiv.org/html/2302.00886v1) | v1 (2023); introduction, approach overview | Video-action captioning precedent |
| [JANUS](https://arxiv.org/abs/2407.08610), [author PDF](https://ojcchar.github.io/files/28-icse24-vid-dupl.pdf) | Abstract, author-hosted introduction/method overview | Visual/OCR/temporal duplicate-video retrieval |
