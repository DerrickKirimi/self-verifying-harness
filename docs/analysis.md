# Analysis of the idea

*Written 17 Oct 2026 from a full read of `docs/idea/` and of the sources in `docs/references.md`. Tags: [SRC] read in a source, [CODE] read in code, [RUN] executed, [INF] inference.*

## 1. What the idea is

`docs/idea/self-verifyingmultimodal-harness.md` is a voice-dictated conversation with an assistant, not a design document. The ideas, in the order the owner raised them **[SRC]**:

1. **Multimodal input to coding harnesses.** Audio (where Whisper Flow fits), an issue described in a video, and after a push, an agent that checks its own work with computer use, browser-use or Playwright. "Combine all this into one solution."
2. **Telephony.** A CPaaS/SIP provider (Twilio, Telnyx) → LiveKit SIP → OpenAI Realtime, or a LiveKit Agents STT → LLM → TTS pipeline. DTMF/USSD triggers. Verification triggered by voice, with the result spoken back.
3. **A remote agent callable without internet** (phone, SMS, USSD) that narrates or works silently and leaves proof (video, screenshots) on a dashboard.
4. **Safety and displays.** A voiceprint as authentication (Safaricom's *Sauti Yako* as the reference) and output on Meta Ray-Bans, Quest or a HUD.
5. **Meetings.** A bot that joins Meet or Zoom, diarises (NeMo), indexes walkthroughs densely, checks the codebase during the meeting and asks clarifying questions. References: Kubrick, the Neural Maze OCR course, AWS's Nova 2 Sonic healthcare appointment agent, Kenya DHA's FHIR eClaims use cases, the LiveKit SIP primer. A second application: a Socratic "gadfly" tutor through the workday. The project began from health research.
6. **Models and hosting.** EmbeddingGemma 2 for everything? Modal vs Lambda vs Kubernetes? When is KEDA needed? APIs vs self-hosting, while still learning to self-host.
7. **The MVP.** Three layers: STT + diarization (the "ear"), reasoning (the "agent"), EmbeddingGemma 2 memory.
8. **Value proposition.** The status quo is meeting → transcriber → manual ticket → developer finds the gap days later. **The owner's key insight is the checkpoint middle ground:** at points during the meeting, the transcriber calls the owner's coding agent to check what's being said against the code, and surfaces questions to ask *before the meeting ends*. And: "What we want is the meeting part."
9. **SaaS framing.** A bot that joins meetings, plus an MCP server that lets the user's coding agent pull from it (and receive pushes).

## 2. What holds

- **The problem is real and the insight is specific.** Context loss between discussion and code, and late discovery that an idea doesn't fit the code or data, are common. The checkpoint idea (check claims against the code *during* the meeting, not after) is the differentiated part. **[INF]**
- **MCP as the boundary between the meeting side and the coding agent is right.** It lets any harness consume the output, so you never have to build or maintain your own IDE agent. Kubrick shows the server-side pattern (tools + resources + versioned prompts) **[CODE]**.
- **Offline first, live later.** The conversation reached this on its own ("start with the listening in the meeting... extensions like LiveKit and telephony later") **[SRC]**. It's the right order.
- **EmbeddingGemma 2 belongs in the retrieval layer, not as the ear.** The conversation got this right, and the model card confirms the specs (§5).

## 3. What's missing: the oracle

The idea never states **what "self-verifying" checks, or against what**. "Run Playwright to confirm the fix" isn't verification unless the check is shown to **fail before** the fix. Otherwise the agent can write a passing test for anything. This is the central design gap. The fix **[INF]**:

1. Extract claims from the recording ("login fails after a password reset", "the API returns 500 on an empty cart", "we can't do X, the schema has no Y").
2. For each claim, write a reproduction (Playwright or pytest) and **run it on the current commit. It must fail.**
3. Only then attempt a fix, and require the reproduction to pass afterwards, with the regression suite still green.
4. Package the result as a **Harbor task**: `instruction.md` from the claim, the clip and frames as context, `tests/` holding the reproduction, `solution/` holding the fix. Gate it with Harbor's oracle/nop check (the oracle solution passes 100%, a no-op scores 0%).

This turns the project into a **generator of verified, multimodal-grounded software tasks**. They feed the owner's RL practice project (`practical_projects_map.md` §12; `harness_stack_deep_dive.md` §14) instead of competing with it. Tasks like these are rare, so they're also the publishable contribution.

## 4. What's wrong or stale in the conversation **[INF unless tagged]**

- **The LiveKit sample code uses the old 0.x API** (`@llm.ai_callable`, `llm.LLM(model=RealtimeModel(...))`), never starts a session, and its tool is a stub that always passes. Current `livekit-agents` is built around `Agent`, `AgentSession` and `@function_tool`. Check the current docs before writing any LiveKit code.
- **The model recommendations are stale for October 2026:** Gemini 1.5 Pro, Claude 3.5 Sonnet, Deepgram Nova-2, Qwen 2.5 Coder. Re-check before choosing.
- **The voiceprint question got no answer, and it matters most.** Voice cloning makes a voiceprint an identifier, not an authenticator. Any write action needs a second factor (`AGENTS.md`, Safety).
- **The HUD/Ray-Ban and SaaS-landing-page threads are premature.** None of them changes whether verification works.
- **The EmbeddingGemma 2 code in `embeddinggemma2-gemma4.md` uses a wrong model id** (`google/embedding-gemma-2-740m-multimodal`); the real id is `google/embeddinggemma-2` **[SRC: Hub]**. Its `model(**inputs).embedding` API is unverified; the model card's quick start uses `sentence-transformers`.

## 5. EmbeddingGemma 2, checked against the model card **[SRC: `google/embeddinggemma-2`, updated 2026-10-06]**

- **Size:** 740M total = 270M text (130M backbone + 140M embedder) + 170M vision + 300M audio encoders, each loadable separately.
- **Output:** 768-d with MRL truncation to 512/256/128; 8,192-token context; mean pooling; Apache-2.0.
- **Benchmarks at 768-d:**

  | Benchmark | Score | EmbeddingGemma 1 |
  |---|---|---|
  | MTEB code v1 | 78.68 | 68.76 |
  | MTEB multilingual v2 | 61.36 | — |
  | MMEB-v2 VisDoc NDCG@5 | 67.84 | — |
  | MMEB-v2 Video Hit@1 | 50.67 | — |
  | MSEB retrieval MRR@10 | 69.54 | — |

- **Truncation:** at 256-d the overall MMEB score drops from 59.01 to 56.24. The card says 128-d "is best suited to text-only workloads".

**Implication [INF]:** it's a strong, local, shared index for code, transcripts, screen frames and audio snippets. A video Hit@1 near 50 means it sits **under** transcript and timestamp search, not in place of transcription or diarization. Measure it on M0 rather than trusting the card.

## 6. What to borrow from each source

**Kubrick (`multimodal-agents-course`, `8dc13da`) [CODE]:**

| Borrow | Change |
|---|---|
| FastMCP server on streamable HTTP owning tools, resources and **versioned prompts** (served from Opik's prompt library) | Your harness is the client; drop its single-round Groq router |
| Pixeltable computed columns: audio → chunks → transcript → embeddings; frames → captions → embeddings | Replace its fixed 45 frames per video with scene-change detection plus speech-aligned sampling; add a screen-OCR column; add an EmbeddingGemma 2 column |
| Trusted arguments (`video_path`, image) injected server-side | Extend to repo path, commit, environment URL |
| Media attachments in traces | Send to one OpenTelemetry backend |
| — | **Avoid its bugs:** `re_encode_video` runs ffmpeg in `finally` (always), and `add_video` inserts the original path and reports success even when nothing was inserted; an empty search result raises `IndexError` |

**Production OCR course (`production-ocr-course`, `4d147f0`) [CODE]:**
- **Borrow:** layout-then-VLM two-stage OCR, applied to screen-share frames of code, slides and terminals; the producer → queue → worker split with a submit-and-poll API; KEDA on `vllm:num_requests_waiting` (later, if ever multi-user); rate limits at the gateway as GPU cost control.
- **Avoid:**
  - the at-most-once queue (`BRPOP` before work, no processing list or visibility timeout);
  - an MCP tool that takes a local `file_path`, which can't work in-cluster (take bytes or a URL);
  - the SSE transport;
  - quoting its throughput claims, which the repo doesn't configure or benchmark.

**Temporal handbook (`kron-k8s-agent`, `1eb10f1`) [CODE]:** durability must match side-effect granularity. Their agent loop is one activity, so a crash replays side effects. Use one activity per stage, and one per side-effecting tool call, with idempotency keys.

**Swarm-tracing article [SRC]:** trace mutations, sample reads, never let tracing block. Use OpenTelemetry GenAI attribute names.

## 7. SPACE and Scion: where they fit

They sit at **different layers**, and neither is a substitute for the other.

**SPACE** (Perplexity, `perplexityai/SPACE`, Apache-2.0, first commit 2026-10-05, 332 commits by `253d8b34` on 2026-10-15) **[SRC: README, docs/architecture.md]**

SPACE is the Sandboxed Platform for Agentic Code Execution:
- **Isolation:** Firecracker microVMs behind an HTTP + SSE API.
- **Model:** a *template* is the starting filesystem; a *sandbox* is a microVM instance with its own writable filesystem; *command sessions* stream process output on a separate data plane with session-scoped attachment tokens.
- **Asynchrony:** lifecycle changes are asynchronous operations you poll.
- **States:** *paused* keeps memory resident; *suspended* snapshots memory, runtime state and root filesystem, then releases resources; sandboxes auto-suspend after 6 h idle.
- **Network:** egress policy with TLS interception and credential injection.
- **Compatibility:** an E2B-compatible wrapper (ECW) is tested with the E2B Python SDK.
- **Deployment:** Kubernetes (Kind locally, EKS reference) or a direct adapter.
- **Host requirements:** x86_64 Linux with `/dev/kvm`, `/dev/net/tun`, loop devices, btrfs and privileged Docker. The install scripts assume an apt-based host **[SRC: docs/installation.md]**. This laptop has `/dev/kvm` but runs Manjaro, so expect install friction **[RUN: `ls /dev/kvm`]**.

**Fit [INF]:** SPACE is the **verification sandbox** at M4+:
- a template per repo at a pinned commit;
- a *suspended* snapshot of the buggy state to restore for every reproduction attempt (cheap, identical starting state);
- egress allowlists, so generated code can't exfiltrate;
- credential injection, so secrets never enter the agent's context.

Through ECW, anything that speaks E2B might run on it, possibly including Harbor's E2B environment (untested). For M0–M3, plain Docker is enough. Keep a small `Executor` interface so SPACE slots in later.

**Scion** (Google, `GoogleCloudPlatform/scion`, Apache-2.0, pre-1.0, `v0.3.0-preview.3` and nightlies; local fork fast-forwarded to `3fc3b040e`, 2026-10-17) **[SRC: README, docs-site philosophy and supported-harnesses]**

Scion is "an open foundation for agent collaboration":
- **Agents:** teams of harness agents (Claude Code, Codex, OpenCode, Gemini CLI, Antigravity, Copilot, Hermes and others, as declarative bundles under `harnesses/`), each in a container with its own credentials, using shared directories, git worktrees or clones.
- **Control plane:** a Hub (local Workstation server, or hosted).
- **Collaboration:** agents message each other and humans via web chat, Telegram, Discord, Slack, Google Chat and Teams; an A2A bridge; agents learn the `scion` CLI through `--help` as a progressive skill.
- **Runtimes:** Docker, Podman, Apple Container, Kubernetes, Cloud Run.
- **Philosophy:** "less is more", "isolation over constraints" (agents run in yolo mode inside containers).

**Fit [INF]:** Scion is the **multi-agent and channel layer** at M5–M6, not the MVP. Roles (listener, claim extractor, checker, reproducer, fixer, verifier) can map to separate agents, and the chat gateways give a "notify me / ask me" channel long before telephony. Its runtimes don't include SPACE. A SPACE runtime for Scion would be new work, and a possible contribution.

**On "Scion vs Anthropic's Sion":** no local source here describes an Anthropic product called "Sion", so this repo makes no claim about it. Add a link to `docs/references.md` and compare from that. As read here, Scion is closer to multi-agent orchestration (agents, messaging, roles) than to SPACE (a sandbox substrate).

## 8. Biggest risks **[INF]**

1. **Reproduction rate.** Writing a reproduction that fails for the right reason from a short clip is hard. M3's gate measures it directly. If it's low, narrow the scope to UI bugs with a visible symptom.
2. **Eval set size.** 10–20 walkthroughs give wide intervals. Use them as a smoke test and a direction check, not a benchmark, until the set grows.
3. **Scope creep** into telephony, HUDs and SaaS before M3 passes.
4. **Privacy.** Real meetings contain other people. Keep the eval set to the owner's own recordings of apps the owner controls.
