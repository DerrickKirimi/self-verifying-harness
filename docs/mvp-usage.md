# Running the development MVP

[CODE] For a single command that retrieves recording frames and replays the
verified generated repair without Gemini calls, start with the
[README demo](../README.md#try-the-recording-to-repair-demo). The commands below
cover fresh model-backed work and individual stages.

[CODE/RUN] M0/M1 and refined numerical M2 checks are measured. Generated M3 checks are being evaluated. Case1679 now has an observed
generated fail/pass repair, independent regressions, wrong-fix controls and real
Harbor nop/oracle rewards0/1. The all-case gate remains incomplete. Independent human claim adjudication remains outstanding. See `STATUS.md`.

## Setup

[CODE] Python >=3.11, uv, ffmpeg/ffprobe and Docker are required. The first
application adapter supports prepared BPMN-js/Karma images with source history at
`/testbed` and installed browser dependencies at `/testbed/node_modules`.
Agent code runs in restricted, network-disabled containers, not the owner checkout.

```sh
uv sync --locked --extra agent
uv run --extra agent python -I -m pytest -q
```

[CODE] Budgeted Gemini configuration uses an owner-only `.env` containing
`SVH_GEMINI_SECRETS_FILE=/absolute/private/credentials.env` and
`SVH_API_CAP_USD=4.00` or a smaller limit. The pointed-to owner-only file contains
`GEMINI_API_KEY`. Never source it as shell code or commit either file. Model access,
limits and dated pricing must be reviewed in `notes/runs/gemini-model-metadata.json`;
the transport rejects stale reviews. Ledger reservations persist across failures.

```sh
uv run --extra agent svh budget
```

## Ordinary input, without benchmark gold

[CODE] Create a private manifest under ignored `data/runtime/`. Recording paths
are relative to that manifest; image and commit are trusted owner configuration.
Compute the actual recording SHA256 and use an immutable prepared image digest.
Do not use a moving image tag. Example structure (replace placeholders):

```json
{
  "format": "svh.task.v1",
  "id": "my-recording",
  "problem_statement": "Observed behavior and the intended requirement.",
  "environment": {
    "adapter": "bpmn-karma-v1",
    "image": "registry/image@sha256:<64 hex characters>",
    "base_commit": "<40 hex characters>"
  },
  "recording": {
    "path": "recording.gif",
    "sha256": "<64 hex characters>",
    "source_url": "owner-local"
  }
}
```

[CODE] Registration checks the source bytes and probes its duration/audio streams.
The recording is limited to 128 MiB and one hour in this initial adapter. No gold
source patch, supplied test, benchmark row or passing admission is required.
Read-only MCP can serve this ordinary task without a model key:

```sh
uv run --extra agent svh mcp --task-manifest data/runtime/task.json --port 8765
```

[CODE] The server uses an owner-only bearer token in `data/runtime/mcp.token`.
The thin client preserves image/structured evidence. Tools/resources/prompts and
trusted input limits are documented in `notes/2026-10-20-mcp-boundary.md`.

## Generated checks and repairs

[CODE] The stage runner keeps the existing deepagents SDK loop. It can extract
claims and inspect code from an ordinary task before generating its check:

```sh
.venv/bin/python -I scripts/run_m3.py --task-manifest data/runtime/task.json \
  --run-name my-run --stage reproduce --model gemini-3.5-flash-lite
```

[CODE/INF] Inspect the retained `candidate.json`, actual browser observation and
recording. A setup assertion is not the target failure. An explicit
`alignment-review.json` beside the frozen `check.js` must bind its SHA256, contain
`"aligned": true` and identify the reviewer/reason before repair. This development
checkpoint is explicit; it is not automatically human-adjudicated. Do not approve
an assertion merely because it failed.

```sh
.venv/bin/python -I scripts/run_m3.py --task-manifest data/runtime/task.json \
  --run-name my-run --stage repair --model gemini-3.5-flash-lite
```

[CODE] Repair is blocked until a completed base Chrome assertion failure and
matching alignment review exist. It transfers source-file bytes to a fresh
container, reruns the identical check and runs native regressions separately.
An invalid first check may get `--candidate 2`; earlier attempts remain retained.
Never modify a frozen check in place or relabel a setup failure as reproduction.
Private run outputs, model traces and recordings stay ignored.

[CODE] Resume with the same manifest, run name and stage. The run binds its input
identity before extraction or any paid call, including interruptions before the
first report is written. A changed manifest needs a new run name. Older ordinary
run directories without an input identity are rejected; preserve them and start
a new run rather than importing an unbound checkpoint.

[CODE] For the frozen public evaluation adapter, replace `--task-manifest` with
`--only swebench-bpmn-<id>`; all eleven corpus rows remain in its report. It
revalidates corpus provenance and keeps benchmark source/test solutions out of
generation. Model refinements, source grounding and actual verification are
separate measurements.

[CODE/INF] Harbor export code requires generated fail/pass plus independent
regressions, pins exact generated source/check bytes and uses a separate verifier.
Packaging is not a trial result. Actual nop=0/oracle=1 must still be executed for
every eventual exported task. No live meeting, SaaS, cloud migration or RL
training system is included in this development MVP.

## Replaying the exported development task

[RUN/CODE] The first verified package is
`tasks/generated-v1/swebench-bpmn-1679`. Its actual integrity report is
`notes/runs/harbor-generated-v1-1679-buildx.json`. Media is reference-only;
source/check bytes and upstream license are bundled. This is a recording-grounded
task, not a claim of multimodal student-agent performance.

[CODE] Harbor is installed separately from the main model/harness environment.
The inspected source checkout/version is recorded in `docs/references.md`.
Its Docker backend also needs Buildx; `scripts/install_buildx.py` installs the
reviewed official binary under ignored project paths and verifies its digests.
After installing Harbor into `data/runtime/harbor-venv`, replay with a new run name:

```sh
.venv/bin/python -I scripts/install_buildx.py
.venv/bin/python -I scripts/run_harbor_integrity.py \
  --task tasks/generated-v1/swebench-bpmn-1679 --run-name my-integrity-replay
```

[CODE] The launcher strips model credentials, runs nop and oracle sequentially,
and rejects missing/setup/timeout rewards or a reward0 without the expected
completed browser assertion failure. The separate verifier accepts only source
artifacts, reruns the primary and independently frozen varied-ID check, then
requires unchanged native regression coverage/skips.
