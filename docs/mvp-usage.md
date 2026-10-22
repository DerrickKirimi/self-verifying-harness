# Running the development MVP

[CODE] For a single command that retrieves recording frames and replays the
verified generated repair without Gemini calls, start with the
[README demo](../README.md#try-the-recording-to-repair-demo). The commands below
cover fresh model-backed work and individual stages.

[RUN] M0/M1 and refined numerical M2 checks are measured. The completed,
financially amended eleven-case v5 run passes the numerical M3 gate:5/11 valid
fail/pass pairs (Wilson95% [21.27%,71.99%]),4/11 full native-passing repairs
([15.17%,64.62%]),zero pending stages. Four distinct public task bundles have
actual Harbor nop/oracle rewards0/1; the1679 and1640 packages also have finite
wrong-fix controls. See the [final results](../notes/2026-10-21-m3-standard-submission-v5-results.md).
Independent human claim adjudication remains outstanding; full MVP shipping is
not declared. See [the review handoff](independent-review.md) and `STATUS.md`.

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

[CODE] Additional credit does not reset prior usage. After the owner explicitly
authorizes more spending, record the higher **cumulative** cap with its expected
previous value and a non-secret authorization reference. For example:

```sh
.venv/bin/svh authorize-budget --total-cap-usd 12.00 --expected-cap-usd 4.00 \
  --authorization notes/2026-10-21-funding-authorization.md
```

[CODE/INF] Update `SVH_API_CAP_USD` in the private `.env` to the authorized cap
before starting another worker. Configuration alone cannot raise an existing
ledger. Funding preserves every settled charge and uncertain reservation, rejects
stale/reused amounts and never re-enables an unexpected-overage lock. Keep new
allowance below actual provider balance and monthly headroom; neither is fetched
automatically by the harness. The example records a historical funding event. The latest allowance is recorded
in [the four-dollar authorization](../notes/2026-10-22-four-dollar-authorization.md);
do not reuse either authorization for another increase.

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

[CODE] Audio-only files such as `.wav` use the same manifest; set `recording.path`
to that file and compute its SHA256. For narrated video or audio-only input, the
generation runner first transcribes bounded audio
chunks under the same persistent budget. It saves the transcript in an owner-only
cache bound to the manifest, includes it in claim extraction, and lets the MCP
code checkpoint reinspect it. `get_transcript` becomes available after that stage;
a standalone MCP server started before transcription reports that it is missing.
Silent video makes no transcription call. Spoken requirements and visible facts
remain distinct, and speaker labels are uncertain chunk-local labels. Human
narration accuracy has not yet been measured; the audio data-flow tests use a
deterministic model and synthetic media. Audio-only inputs return `no_video` from
frame/screen-text tools. Their claims cite reported speech, never invented visual
observations; actual software behavior still requires the frozen browser check.

[CODE] The server uses an owner-only bearer token in `data/runtime/mcp.token`.
The thin client preserves image/structured evidence. Tools/resources/prompts and
trusted input limits are documented in `notes/2026-10-20-mcp-boundary.md`.

## Index an ordinary recording

[CODE] With budgeted Gemini configured, this explicit step produces sampled
captions and screen text, plus a transcript when audio exists. It requires no
benchmark rows, gold patches or corpus admission:

```sh
.venv/bin/svh ingest --task-manifest data/runtime/task.json
```

[CODE] For audio-only input, ingestion transcribes the audio and `find_moment`
searches timestamped transcript segments using lexical FTS5. It makes no visual
captioning call. Omit `--semantic` for that route; this option currently embeds
visual captions. Audio retrieval quality is not established by the visual M1 gate.

[CODE/INF] Restart the MCP server after ingestion. Its `find_moment` and
`get_screen_text` tools now read the manifest-bound private index. The default
search is the small lexical baseline; captions and screen text are fallible model
outputs and must be checked against frames. Ingestion resumes from retained
responses without regenerating them. Changing the manifest creates a new cache.

[CODE] To select the local text-embedding retrieval measured at M1, install the
`agent` and `retrieval` extras and prepare the pinned local model using the
[M1 setup instructions](../notes/2026-10-20-m1-complete.md#reproduce-the-selected-local-retrieval).
Then run:

```sh
.venv/bin/svh ingest --task-manifest data/runtime/task.json --semantic
```

[CODE/INF] Embedding inference runs locally and has no Gemini charge. This option
reuses saved captions; it fails if the reviewed local model is missing. The
ordinary-task route has not received a separate retrieval quality evaluation;
M1's eleven-case development-set result does not measure a new recording.

[CODE] Check actual MCP metadata, frames, search and screen-text retrieval after
indexing (no model call; choose a fresh output path on every run):

```sh
.venv/bin/python -I scripts/smoke_task_evidence.py \
  --task-manifest data/runtime/task.json --output data/runtime/evidence-smoke.json
```

[CODE] To exercise audio-only provider transcription and actual MCP with a
controlled synthetic narrator, install `espeak` and use the budgeted smoke below.
This makes a Gemini transcription call on its first run and retains the response
for resume. It reports functional behavior, not human narration accuracy:

```sh
.venv/bin/python -I scripts/smoke_audio_only.py --run-name my-audio-smoke \
  --output data/runtime/my-audio-smoke.json
```

## Generated checks and repairs

[CODE] The stage runner keeps the existing deepagents SDK loop. It can extract
claims and inspect code from an ordinary task before generating its check:

```sh
.venv/bin/python -I scripts/run_m3.py --task-manifest data/runtime/task.json \
  --run-name my-run --stage reproduce --model gemini-3.5-flash-lite
```

[CODE/SRC] The default service tier is Standard. To use the separately reviewed
Flex tier, add `--service-tier flex --thinking medium` to **both** stage commands.
Flex requires fresh access metadata bound to `notes/runs/gemini-price-policy.json`,
which contains separately reviewed Standard and Flex rates;
the transport reserves the full input-context limit plus maximum output at the
matching reviewed prices. It permits one request attempt, a fifteen-minute
timeout, and no automatic Standard fallback. Queuing can make a stage take longer.
See the [reviewed policy and actual access smoke](../notes/2026-10-21-next-evaluation-budget-options.md).
Never increase or reset the persistent cap to get around a rejected reservation.

[CODE/INF] Inspect the retained `candidate.json`, actual browser observation and
recording. A setup assertion is not the target failure. An explicit
`alignment-review.json` beside the frozen `check.js` must bind its SHA256, contain
`"aligned": true` and identify the reviewer/reason before repair. This development
checkpoint is explicit; it is not automatically human-adjudicated. Do not approve
an assertion merely because it failed.

[CODE] For the example task ID `my-recording`, the exact files are under
`data/runtime/m3/my-run/my-recording/1/`. Read `check.js`, `candidate.json` and
`pre/observation.json`; `pre/console.log` retains the raw browser output.
The review JSON needs `check_sha256` (the actual SHA256 of `check.js`), `aligned`
(a boolean), `reviewer` and `reason`. Explain why the observed failure is the
recorded target and why initial setup succeeded. Use `aligned:false` when it
does not match; the repair stage will reject it. Never edit the frozen check to
make an existing review pass.

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

[CODE] Preparation failures are recorded in `report.json` with their phase and
error types. Code-checkpoint attempts retain separate
`checkpoint-attempts/<number>/trace.json` and MCP logs; an explicit CLI resume
starts another attempt without overwriting the failure. Saved extraction is
reused. Successful checkpoints are hash-bound to the report and rejected if
changed. Audio checkpoints must obtain metadata/transcript evidence before their
typed final and have five bounded source-tool replies. An empty or unresolved
primary requirement abstains before reproduction. When extraction itself is
unclear, its questions are printed before entering code inspection. Supply an
explicit clarification in a new manifest/run rather than editing a frozen check.

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

[CODE] After a full generated repair and native regressions pass, export an
ordinary run and execute its real integrity trials:

```sh
.venv/bin/python -I scripts/export_m3.py --task-manifest data/runtime/task.json \
  --run-directory data/runtime/m3/my-run --output-directory data/runtime/exports/my-run
.venv/bin/python -I scripts/run_harbor_integrity.py \
  --task data/runtime/exports/my-run/my-recording --run-name my-run-integrity
```

[CODE] Keep private exports under ignored paths. Export refuses an existing task
directory; use a new destination instead of overwriting evidence. The ordinary
route uses the observed native baseline and never loads benchmark gold patches.
For public evaluation exports, omit `--task-manifest`; `--only <case-id>` selects
one completed case so a repeated experiment need not duplicate the same claim.

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

### Renew Gemini access and pricing reviews

Paid calls fail closed when either authenticated model access or the operator's
price review is older than 24 hours. Renewal does not reset or raise the budget.
Read the current [official pricing](https://ai.google.dev/gemini-api/docs/pricing),
including Standard/Flex rates and any dated promotional changes. Then update
`notes/runs/gemini-price-policy.json` with the actual UTC review timestamp and a
short review note. Do not merely refresh a timestamp without reading the prices.
Rates are checked against the reviewed allowlist in `src/svh/model_policy.py`;
changed prices require a code review before paid usage resumes.

Run `.venv/bin/python -I scripts/probe_gemini.py`. It fetches authenticated model
metadata, checks exact model names, generation capability and positive token
limits, and atomically replaces access evidence only after both models succeed.
It retains the previous evidence under its SHA256 filename. The new evidence
binds the exact price-policy bytes. No inference, upload or token-count request
is made. Price and access reviews can have different UTC dates, but both must
remain within 24 hours. Recheck `.venv/bin/python -I -m svh.cli budget` afterward.

Source edit outputs accept relative `lib/...js` or the exact equivalent
`/workspace/lib/...js` used by read tools. Other absolute roots, traversal,
noncanonical paths and non-JavaScript files are rejected before source reads;
old/new replacements must still match exactly once and change content.
A new reproduction stage is refused before model/MCP setup once two distinct
check versions are recorded for that case. Trusted replays of identical frozen
bytes remain possible. Maintenance replays do not revise historical eval scores.
