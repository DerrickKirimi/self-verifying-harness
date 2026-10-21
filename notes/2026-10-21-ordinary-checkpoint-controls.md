# Enforce evidence and retain ordinary preparation failures

[RUN] The first real ordinary audio run (`ordinary-audio-v1`) omitted actual
transcript reinspection. The existing postcondition refused to continue before
any reproduction/fix. The second (`ordinary-audio-v2`) obtained the transcript but
ignored prompt-only source-read limits and reached GraphRecursionError before
completing. A typed reply in its retained trace also asks about a garbled technical
phrase. Neither run is a successful end-to-end result. Evidence hashes/tool replies:
`notes/runs/ordinary-audio-development-failures.json`.

[CODE] For audio input, middleware in the existing deepagents SDK now requires
successful metadata and transcript tools before source inspection or a typed final.
It then allows five source-tool replies, scopes reads/searches to `/workspace/lib`,
forces grep content output and denies writes/arbitrary execute/delegation. After
the source budget it exposes only the typed checkpoint. Existing silent-corpus
checkpoint paths and the public M3 method/rubric are unchanged.

[CODE] Ordinary preparation records its current phase and budget before paid
work. Errors preserve a report and separate numbered checkpoint attempt traces;
explicit resumes cannot overwrite the old model response. A successful checkpoint
is hash-bound before use, and an empty/unresolved primary requirement abstains.
The worker lock is explicitly released on exit. No new reasoning loop or implicit
provider retry was introduced.

[RUN] Full suite: **114 passed**, `.venv/bin/python -I -m pytest -q`. Added tests
cover missing/failed evidence, source-budget exhaustion, scoped reads/write
rejection, retained failed attempts, extraction reuse and changed-checkpoint
rejection.

[RUN/INF] The controlled fixture author supplied an explicit new-manifest
clarification of `task.di.label`; the unclarified audio and failed outputs remain
unchanged. This is a documented change of input, not a silent correction to a
model transcript or a new public-corpus evaluation item. `ordinary-audio-v3`
then completed extraction and code checkpoint with `expected_source=issue` and
observed its generated target property assertion fail on buggy source. Source
repair then made the identical check pass; original and repaired native suites
each complete1779 tests with1772 passes and seven unchanged skips. No supplied
benchmark source/test patch was used. Proof and native baseline hashes:
`notes/runs/ordinary-audio-v3-generated-repair.json`. Harbor packaging/integrity
is tracked separately. No human speech accuracy is established by this synthetic
development exercise; it is not pooled into the public evaluation denominator.
