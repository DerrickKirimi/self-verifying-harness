# Multimodal self-verifying harness

Turn claims about software, spoken or shown in a meeting recording, a bug-walkthrough video or (later) a phone call, into executable checks. Then use those checks to verify an agent's fix.

```text
 recording ─► INGEST ─► CLAIMS ─► CHECKPOINT ─► VERIFY ─► PROOF + HARBOR TASK
            transcript,  "login fails   is it consistent   repro must FAIL   clip, frames, trace,
            frames,      after reset"   with the code?     before the fix,   Playwright trace,
            screen OCR,                 → questions to     PASS after it     test, diff
            embeddings                    ask in the meeting
```

**Status:** M0 passed on eleven reviewed temporal cases with observed supplied
test failures before and passes after their reference fixes. The visual corpus
is frozen; M1 and refined numerical M2 checks are measured. M3 now has one generated recording-to-check-to-fix demonstration, independent
regressions and executed Harbor nop/oracle rewards0/1. The all-case evaluation
is still incomplete; the MVP is not yet shipped. Independent human claim
adjudication is outstanding. See the [development usage guide](docs/mvp-usage.md).
See [`STATUS.md`](STATUS.md).

## Run the first checkpoint

Requires Python 3.11+, `uv` and access to a running Docker daemon. No model API
key is needed.

```sh
uv sync --locked
docker build -t svh-eval:local sandbox
uv run svh verify
uv run svh serve --revision pre
```

The last command serves the recording fixture at `http://127.0.0.1:8080`.
See the [recording guide](docs/recording-guide.md) for the three walkthroughs.
Run the runner's own tests with `uv run python -I -m pytest`.

The fixture oracle freezes the same tests for both Git revisions, runs each
inside restricted Docker containers, rejects setup errors as evidence, and
writes commit IDs, image ID, test hashes, logs and a Wilson interval to
`notes/runs/fixture-oracle.json`. This is a fixture check, not the M0 completion
gate or a Harbor oracle/nop run.

Reference projects inform decisions; none is a required base. The M0 runner
works independently of the optional agent/MCP stack. No Pixeltable or embedding
model is inherited from a reference. Current
integration and retrieval decisions are in [the decision log](docs/decisions.md).

The first external oracle also works: a SWE-bench Multimodal BPMN video task
fails at the expected color assertion before its reference fix, then passes
its 1777 executed tests afterward (7 existing skips remain unchanged).
The full M0 set now contains eleven admitted cases: 11/11, Wilson 95%
[74.12%, 100%], frozen in [evals/frozen-m0.json](evals/frozen-m0.json).
This measures curated supplied-oracle integrity, not generated fixes or speech.
See the [audit and reproduction commands](notes/2026-10-20-swebench-multimodal-pilot.md)
and [external admission workflow](notes/2026-10-20-external-admission.md).

## Why

Today the path runs: meeting → transcriber → someone writes a text ticket → a developer finds the gap days later. Context gets lost at every step, and "the fix works" usually means a test written after the fix that has only ever been seen passing. This project keeps the recording's evidence attached to the work and insists on a reproduction that fails first.

## Read in this order

1. [`docs/idea/`](docs/idea/): the original idea, verbatim.
2. [`docs/analysis.md`](docs/analysis.md): what holds, what's missing, what's wrong, and how SPACE and Scion fit.
3. [`docs/roadmap.md`](docs/roadmap.md): milestones M0–M6, each with a measurable gate.
4. [`docs/decisions.md`](docs/decisions.md): decisions and open questions.
5. [`docs/references.md`](docs/references.md): sources, with local clones and commits.
6. [`AGENTS.md`](AGENTS.md): rules for anyone (human or agent) working here.
7. [`docs/literature-review.md`](docs/literature-review.md): related work ranked
   by relevance, including SWE-bench Multimodal successors, video replay and
   browser verification, with concrete cautions for our design.

## Layout

```text
AGENTS.md / CLAUDE.md   instructions for agents (CLAUDE.md imports AGENTS.md)
STATUS.md               current state and the next step, updated every session
docs/idea/              the owner's original idea, verbatim (never edited)
docs/                   analysis, roadmap, decisions, references
evals/                  the M0 evaluation set: schema now, recordings and annotations later
notes/                  working notes and experiment logs
```
