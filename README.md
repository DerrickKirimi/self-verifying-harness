# Multimodal self-verifying harness

Turn claims about software, spoken or shown in a meeting recording, a bug-walkthrough video or (later) a phone call, into executable checks. Then use those checks to verify an agent's fix.

```text
 recording ─► INGEST ─► CLAIMS ─► CHECKPOINT ─► VERIFY ─► PROOF + HARBOR TASK
            transcript,  "login fails   is it consistent   repro must FAIL   clip, frames, trace,
            frames,      after reset"   with the code?     before the fix,   Playwright trace,
            screen OCR,                 → questions to     PASS after it     test, diff
            embeddings                    ask in the meeting
```

**Status:** bootstrapping. No code yet; the first milestone is the evaluation set (M0). See [`STATUS.md`](STATUS.md).

## Why

Today the path runs: meeting → transcriber → someone writes a text ticket → a developer finds the gap days later. Context gets lost at every step, and "the fix works" usually means a test written after the fix that has only ever been seen passing. This project keeps the recording's evidence attached to the work and insists on a reproduction that fails first.

## Read in this order

1. [`docs/idea/`](docs/idea/): the original idea, verbatim.
2. [`docs/analysis.md`](docs/analysis.md): what holds, what's missing, what's wrong, and how SPACE and Scion fit.
3. [`docs/roadmap.md`](docs/roadmap.md): milestones M0–M6, each with a measurable gate.
4. [`docs/decisions.md`](docs/decisions.md): decisions and open questions.
5. [`docs/references.md`](docs/references.md): sources, with local clones and commits.
6. [`AGENTS.md`](AGENTS.md): rules for anyone (human or agent) working here.

## Layout

```text
AGENTS.md / CLAUDE.md   instructions for agents (CLAUDE.md imports AGENTS.md)
STATUS.md               current state and the next step, updated every session
docs/idea/              the owner's original idea, verbatim (never edited)
docs/                   analysis, roadmap, decisions, references
evals/                  the M0 evaluation set: schema now, recordings and annotations later
notes/                  working notes and experiment logs
```
