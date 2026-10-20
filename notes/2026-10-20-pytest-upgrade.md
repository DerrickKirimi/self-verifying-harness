# Patched pytest in the host and fixture sandbox

[SRC/RUN] GitHub reported three open moderate alerts, all GHSA-6w46-j5rx-g56g
(CVE-2025-71176), against pytest in `pyproject.toml`, `uv.lock` and
`sandbox/requirements.txt`. Snapshot:
`notes/runs/dependency-alerts-before.json`. The issue concerns insecure temporary
directory handling; the first patched release is 9.0.3, confirmed by the
[upstream release notes](https://github.com/pytest-dev/pytest/releases/tag/9.0.3).

[CODE/RUN] Changed the supported pytest range to `>=9.0.3,<10`; uv selected
9.1.1 on 2026-10-20. The sandbox pins the same release. Synced the locked host
environment with the dataset extra, built `svh-eval:pytest9`, and observed all
51 harness tests pass under the new host pytest. No new test cases were needed
for this dependency-only change.

[RUN] Executed the original three frozen fixture checks against the original
buggy/fixed app commits in the new sandbox. All three failed by assertion before
and passed afterward: 3/3, Wilson 95% [43.85%, 100%]. New proof:
`notes/runs/fixture-oracle-pytest9.json`. Compared `test_sha256` with the original
report and confirmed every check is byte-identical. This is fixture regression
evidence, not additional temporal M0 cases.

[RUN] New image ID:
`sha256:c6851f11372980d302814879a150a90fbe1400f6ce3a6b019dd7deba7307b602`.
Promoted it to `svh-eval:local` after verification; the old proof remains intact.
The ongoing SWE-bench batch uses separate immutable images and was unaffected.

[INF] Updated declarations address the specified version range; remote alert
closure must be checked after GitHub reprocesses the push. This is not a general
security audit of third-party benchmark images.
