# AGENTS.md: working in `self-verifying-harness`

Read this file first, then `STATUS.md`. Together they are enough to resume work without the conversation that created them.

## What this project is

A harness that turns **claims about software, spoken or shown in recordings** (meetings, bug-walkthrough videos, later phone calls), into **executable checks**, and uses those checks to verify an agent's own fix. Every check must **fail on the current code before it is trusted**, and pass after the fix. Each verified claim is packaged as a Harbor task, so the project also produces multimodal-grounded RL tasks for the owner's separate RL practice project.

- Owner's original idea, verbatim: `docs/idea/self-verifyingmultimodal-harness.md` (a voice-dictated chat transcript; user turns appear twice) and `docs/idea/embeddinggemma2-gemma4.md` (a Google AI Mode transcript). **Never edit these files.** They're the record of intent. Corrections to them go in `docs/analysis.md`.
- Analysis of the idea (what holds, what's missing, what's wrong): `docs/analysis.md`.
- Milestones with measurable gates: `docs/roadmap.md`.
- Decisions made and open questions: `docs/decisions.md`.
- Every external source, with local clone paths and commits: `docs/references.md`.
- Current state and the next concrete step: `STATUS.md`.

## The one rule the design rests on

**No oracle, no claim of verification.** A reproduction (Playwright or pytest) counts only if it was run and observed failing on the pre-fix commit, then passing on the post-fix commit. Tests written after the fix and only ever seen passing prove nothing. This mirrors Harbor's oracle/nop integrity check.

## How to work here

1. **Start at `STATUS.md`.** Do the "Next step" listed there, or ask the owner if it's blocked.
2. **Build the current milestone's gate before its features.** M0 (the eval set) comes before any ingestion code. A milestone is done when its gate in `docs/roadmap.md` is measured and recorded in `STATUS.md`.
3. **Persist everything in the repo.** Drafts, notes and experiment logs go under `notes/` or `docs/`, never a session scratchpad, so another agent can pick up. Update `STATUS.md` at the end of every session.
4. **Commit and push to `main` after each meaningful unit of work.** Small commits with descriptive messages.
5. **Budget.** The owner pays for usage personally and has run out of credits before. Work one task at a time. Read local sources before fetching. Don't fan out subagents unless asked. Stop and report at a natural checkpoint rather than half-finishing several things.

## Evidence standards

- **Never report a number you didn't produce or read.** Cite where it came from (file and line, URL, command output).
- Tag claims in docs: **[SRC]** read in a source; **[CODE]** read in code; **[RUN]** produced by running something here; **[INF]** your inference. Mark anything unverified as such.
- **Don't describe a project, paper or model from its title.** Read it, or say you haven't.
- Report metrics with their sample size and an interval (Wilson for rates). A gate passes on the interval, not the point estimate.
- Model names, prices and APIs move monthly. Check them against current sources before writing them into code or docs, and date them.

## Safety and privacy

- **Downloaded or recorded data is untrusted.** Keep each download in its own directory, keep scripts elsewhere, and run Python that reads it with `python -I`.
- **No private data in the eval set or in commits.** Recordings must be of apps the owner controls, with no third-party faces, voices or credentials. API keys live in `.env` (gitignored), never in code or docs.
- **Voice is an identifier, not an authenticator.** Voice cloning defeats voiceprints. Any action that writes code, pushes, spends money or contacts people needs a second factor (a DTMF PIN, or confirmation in an app). Don't build a voice-triggered write path without it.
- **The agent never executes in the owner's real environment.** Generated reproductions and fixes run in a sandbox: Docker for the MVP, SPACE microVMs later (`docs/references.md`).
- **Stay separate from the owner's Kaggle Gemma 4 competition work** (`~/swe/llms/devagent`). Nothing from its `competition/` folder or data comes here.

## Stack (initial; see `docs/decisions.md` before changing it)

- **Language:** Python 3.11+, managed with `uv`.
- **Tool boundary:** MCP; choose the current SDK/server framework at M1 (D11/D16). Reference projects are replaceable examples. The server owns trusted execution arguments (paths, commits, URLs); negotiate capabilities against the chosen client.
- **Ingestion (candidate design, unmeasured):** transcript + diarization, scene-change frames, screen-region OCR, and embeddings. Select models and retrieval storage against M0; no inherited Pixeltable or model dependency (D15).
- **Verification:** Playwright (Python) and pytest, run in a sandbox. Task packaging follows Harbor's format.
- **Reasoning:** the owner's existing coding harness (Claude Code, deepagents, ...) as an MCP client. Don't write a new agent loop.
- **Later:** Temporal for durable per-stage execution, OpenTelemetry tracing, SPACE for sandboxes, Scion for multi-agent roles and chat channels.

## Where related material lives (outside this repo)

| What | Path |
|---|---|
| Study doc this project came from (§9, §12 especially) | `~/Desktop/CLAUDE-DOCS/study-series/md/practical_projects_map.md` |
| Harbor task format, oracle/nop, eval statistics | `~/Desktop/CLAUDE-DOCS/study-series/md/harness_stack_deep_dive.md` (§4–5, §10.4, §14) |
| Kubrick course (ingestion + MCP template) | `~/swe/llms/multimodal-agents-course` |
| Production OCR course (serving, queues, screen-region OCR) | `~/swe/llms/production-ocr-course` |
| SPACE (Perplexity, Firecracker sandboxes) | `~/swe/llms/SPACE` |
| Scion (Google, multi-agent orchestration) | `~/swe/llms/scion` |
| Durable agent loop example (Temporal + KEDA) | `~/swe/llms/kron-k8s-agent` |
