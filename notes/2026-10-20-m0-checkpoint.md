# First executable M0 checkpoint

- [RUN] `uv sync --locked`: installed the package and locked dependencies.
  The host environment selected CPython 3.13.7; sandbox base is Python 3.12.
- [RUN] `docker build -t svh-eval:local sandbox`: successful. Base digest and
  dependency versions are in `sandbox/Dockerfile` and `sandbox/requirements.txt`.
- [RUN] `.venv/bin/python -I -m pytest`: **22 passed in 0.09s** on the final
  checked code. These cover oracle result classification, sample duplication,
  traversal rejection, Wilson interval behaviour, and annotation structure/files/times.
- [RUN] `.venv/bin/python -I -m svh.cli verify`: **3/3 verified fixtures**, 95%
  Wilson interval **[0.4385029682449546, 1.0]**. Full evidence:
  `notes/runs/fixture-oracle.json`. Both revisions ran with the same image ID
  and frozen reproduction files. All pre-fix outcomes are assertion failures;
  all post-fix outcomes are passes.
- [RUN] HTTP smoke checks started `svh serve --revision pre` and `post`, queried
  `/?q=login`, and observed HTTP 200 with `0 issues` before / `1 issues` after.
  Output: `notes/runs/recording-server-smoke.json`. This checks served HTML,
  not browser rendering. The readiness probe initially encountered Docker's
  transient connection reset; retrying readiness through that startup window
  completed successfully. Both servers were interrupted and cleaned up.
- [RUN] `git diff --check`: clean. No temporary containers were listed by
  `docker ps --filter name=svh- --format '{{.Names}}'` after the checks.

## Scope and next step

- [CODE] App fixes and reproductions are hand-written. No coding agent or model
  was invoked by the product. There is no ingestion pipeline or Harbor export.
- [CODE] Annotation validation does not decode recordings or verify speech.
  Fixture reports deliberately do not fill annotated walkthrough `observed` fields.
- [INF] The current sandbox and oracle target controlled M0 fixtures. The later
  agent-facing execution service needs an additional threat/integrity review
  before treating hostile generated app/test code as trustworthy evidence.
- [SRC] The owner asked to avoid inherited reference-project architecture.
  D11–D16 document replaceable references, current MCP capability checks and
  measurement-led retrieval selection. No Pixeltable dependency was introduced.
- [INF] Natural handoff: owner records the first three clips using
  `docs/recording-guide.md`; next code unit binds validated annotations and
  recording hashes to oracle reports and expands the set to 10–20 bugs.
  M0 is incomplete until that full gate is measured. The full MVP is not shipped.
