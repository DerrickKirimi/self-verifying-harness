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
is frozen; M1 and refined numerical M2 checks are measured. M3 now has two distinct generated recording-to-check-to-fix demonstrations,
independent regressions and executed Harbor nop/oracle rewards0/1 for each.
The [completed all-eleven run](notes/runs/m3-probed-v2-final-score.json) verifies2/11 (Wilson95%
[5.14%,47.70%]) and fails the acceptance gate; the MVP is not yet shipped. An
ordinary clarified synthetic audio run also completes generated repair and
Harbor integrity. A [later evaluation](notes/2026-10-21-m3-mapped-flex-v3-results.md)
retains a provider error and local budget exhaustion; it adds no verified repair.
Independent human claim
adjudication is outstanding. See the [development usage guide](docs/mvp-usage.md).
See [`STATUS.md`](STATUS.md).

## Try the recording-to-repair demo

Requires Linux x86_64, Python 3.13, `uv`, `ffmpeg`/`ffprobe`, and a running
Docker daemon. Run these commands from this repository. The isolated Harbor
installation is needed once (it requires Python >=3.12):

```sh
uv sync --locked --extra agent --python 3.13
uv venv --python 3.13 data/runtime/harbor-venv
uv pip install --python data/runtime/harbor-venv/bin/python \
  'harbor @ git+https://github.com/harbor-framework/harbor.git@4b94505a91c5ddcb70b5740ac95718ddee13e5a0'
.venv/bin/python -I scripts/demo.py
```

On this workspace the environments are already installed; just run the last
command. No Gemini key or paid model call is needed. The first run downloads the
reviewed public GIF and Docker image; allow several minutes and disk space for
the prepared browser environment. Buildx is installed under this project's
ignored data directory with pinned official checksums.

The demo retrieves three real recording frames through authenticated MCP, then
replays the previously generated check and source fix in fresh Docker Harbor
trials. Expected result: `nop` reward **0** from the target assertion failing;
`oracle` reward **1** after the generated fix, with the same check, an independent
variant and native regressions passing. This replays frozen generation outputs;
it does not ask a model to generate a new fix.

The command prints `PASS` and paths to PNG frames and `result.json` under
`data/runtime/demos/<run-name>/`. Detailed rewards and evidence hashes are saved
to `notes/runs/harbor-<run-name>.json`; raw browser observations and logs live in
`data/runtime/harbor-jobs/`. Every invocation gets a fresh run name. A nonzero exit
means the demo did not pass; inspect the printed run directory and logs.

For **your own recording and fresh model-backed generation**, follow
[ordinary input and generation instructions](docs/mvp-usage.md). That path needs
Gemini credentials and the persistent spending cap. The current application
adapter supports prepared BPMN-js/Karma projects; arbitrary repositories and
speech quality are not yet validated.

## Run the original fixture checkpoint

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
8. [`docs/independent-review.md`](docs/independent-review.md): the blank human
   review packet and scoring instructions for the outstanding M2 validation.

## Layout

```text
AGENTS.md / CLAUDE.md   instructions for agents (CLAUDE.md imports AGENTS.md)
STATUS.md               current state and the next step, updated every session
docs/idea/              the owner's original idea, verbatim (never edited)
docs/                   analysis, roadmap, decisions, references
src/svh/                evidence tools, model budget, Docker verification and task packaging
scripts/                end-to-end demo, evaluation, export and integrity commands
evals/                  frozen corpus, annotations, prospective methods and acceptance gates
tasks/                  generated Harbor task packages and their proof manifests
notes/                  working notes and measured experiment reports
data/external/          ignored downloads and reference-only recordings
data/runtime/           ignored private runs, model traces, indexes and browser logs
```
