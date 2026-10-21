# Runnable recording-to-repair replay

[CODE] `scripts/demo.py` is the README entry point. It checks the frozen public
task package, downloads only its previously reviewed GIF into a dedicated ignored
directory, verifies SHA256, creates an ordinary task manifest, and retrieves three
PNG frames through the actual authenticated MCP server. It then executes the real
Harbor nop/oracle launcher. It makes no model calls and requires no Gemini key.
The isolated Harbor environment and project-only pinned Buildx setup are documented
in the README; the Harbor source pin is the inspected local checkout's commit.

[RUN] Executed `.venv/bin/python -I scripts/demo.py --run-name
readme-e2e-20261021` successfully. Full replay report:
`notes/runs/harbor-readme-e2e-20261021.json`. Both original target assertions fail
under nop (reward0); both pass under oracle (reward1), as do the independently
frozen varied-ID checks and native regressions (1792 executed passes, seven skips,
1799 discovered). No infrastructure exception was present. Frames and manifest
remain under `data/runtime/demos/readme-e2e-20261021/`; public evidence hashes are
in `notes/runs/demo-readme-e2e-20261021.json`.

[INF] This demonstrates recording evidence access and executable replay of a
previous model-generated repair. It does not measure fresh model generation,
speech quality, arbitrary repositories, or completion of the eleven-case M3 gate.
The README links the separate model-backed ordinary-input workflow.
