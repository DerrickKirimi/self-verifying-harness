# Matched M2 claim extraction

[CODE] `svh.extract` uses a fixed one-request stage, not a replacement coding
agent loop. `public_tasks` copies only public problem_statement plus trusted
image/base/identifier metadata from an admitted row. Extraction messages contain
only the quoted public issue and optional ordered 45 sampled frames: no gold
claim, native test name, source/test patch, grader or code-checkpoint metadata.
Both conditions use Gemini 3.5 Flash-Lite and the frozen 4096-output-token cap.
Expected behavior must be attributed to issue/shown/unknown; absent video means
no timestamps or visual observations. Uncertainty/questions remain explicit.

[CODE] Raw metered responses are saved before parsing and reused on resume.
All eleven cases remain in each report, including not_attempted/error/abstention
states. Models/prompts/rubric/corpus cannot be silently mixed on resume. A process
lock prevents duplicate extraction workers. No automatic regeneration follows
an invalid output or unknown provider outcome; the shared budget still applies.

[RUN] Pilot 1655 completed both conditions. Issue-only produced one claim with
no source span; temporal media produced one claim citing the visible pale label
text and darker border, with expected behavior explicitly attributed to the
issue. This is an unscored model output, not generated executable verification.
The full matched batch is now running sequentially in exec session 38364; do not
restart it while active. Remaining outputs and judgments are not yet measured.

[RUN] Three tests check field allowlisting, matched input framing, no invented
issue-only timestamps and raw-response reuse without another model request.
The prior full suite passed 80 tests; these three additional tests pass.

[CODE] Run with authorized private configuration and current reviewed prices:

```sh
.venv/bin/python -I scripts/run_m2_extraction.py --only swebench-bpmn-1655
.venv/bin/python -I scripts/run_m2_extraction.py
```

[INF] Next: freeze outputs, review claims against actual source frames without
correcting them, bind judgments to output hashes and calculate the frozen gate.
Run actual Docker/MCP code checkpoints through deepagents after extraction is
terminal; paid requests remain sequential. Code-checkpoint source must stay
unchanged. M2 and the full MVP remain incomplete.
