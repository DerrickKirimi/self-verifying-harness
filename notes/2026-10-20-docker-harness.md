# Docker backend and existing harness boundary

[CODE] `svh.docker_backend.DockerSandbox` implements the selected deepagents
BaseSandbox protocol, not an agent loop. Trusted controller metadata chooses an
immutable image and buggy commit. A separate restricted preparation container
streams `git archive` bytes; the agent gets a fresh one-commit repository under
/workspace, no origin, and an empty tmpfs masking the original /testbed/.git.
No supplied tests, gold patches, grader script, owner directories or credentials
are mounted or passed to the agent container.

[CODE] Image root is read-only. Writable source, /tmp and dependency cache are
bounded tmpfs mounts; dependencies come from the image read-only. Network is
none, all capabilities dropped except SETUID/SETGID required by the existing
browser environment, no-new-privileges, memory 4GiB, CPU2, pids512. Docker logging
is disabled. Captured command output is bounded at 64KiB and excess is discarded.
Commands are argv data to docker exec; their shell runs only inside Docker.
A timeout destroys the execution domain and returns an unknown/infrastructure
exit, never a qualifying assertion failure. File transfer uses bounded JSON/
base64 on stdin and resolves writes under /workspace or /tmp only.

[CODE] Source archive and actual workspace contents are hashed. The latter is
computed with trusted Python inside the container, independently of mutable git
state, so M2 can reject code changes during its inspection checkpoint. The helper
works with the older Python in the benchmark image as well as the host SDK.

[CODE] `svh.harness.create_harness` accepts only an explicit model and running
Docker backend. It registers a model-specific SDK harness profile disabling the
auto-added general-purpose subagent, passes no subagents and blocks fabricated
task dispatch in synchronous/asynchronous middleware. The existing SDK retains
ownership of planning, tool dispatch and summarization; budgeted models cover
all generation paths. Tracing must remain disabled around actual runs.

[RUN] `notes/runs/docker-backend-smoke.json` is an actual public-image Docker
run. It passes fresh-history, hidden host file/environment, read-only root,
working-directory, network-unreachable, byte-exact transfer, output bound,
source-change fingerprint and timeout cleanup checks. The final container is
absent. No model-generated command has executed yet, either here or on the host.
Three deterministic harness tests verify execution dispatch, absent/denied task
delegation and refusal of a host/implicit backend; these doubles establish no
model quality. The full suite passed 80 tests before the final fingerprint
helper addition; the actual smoke verified that addition afterward.

[INF] Next: matched M2 extraction and an actual model-driven code checkpoint.
The checkpoint must preserve the initial source fingerprint and report inspected
locations as evidence/hypotheses, not claim a verified fix. M3 uses a fresh
sandbox and requires a frozen assertion failure before any generated source fix.
