# Roadmap

Each milestone has a **gate**: a measured result, with sample size and interval, recorded in `STATUS.md`. Don't start a milestone's features before the previous gate passes. Estimates assume part-time work alongside a full-time job. **[INF]**

**Timing.** The owner's study plan (`~/Desktop/CLAUDE-DOCS/study-series/md/career_and_reading_plan.md` §5) reserves Nov–mid-Jan for the Gemma paper track, interviews and the Harbor RL practice project. Only M0 is lightweight enough to start before mid-January. M1 onwards is for after that, unless the owner re-plans.

**2026-10-20 update.** The owner explicitly requested starting implementation now.
That supersedes the calendar assumption above, while the milestone gates and
evaluation-first order remain in force. Reference projects are replaceable;
the candidate M1 stack below is a hypothesis to evaluate, not a dependency list
(decisions D11/D15/D16). [SRC/INF]

**M0 sourcing update (D18).** Vetted public video/task pairs may substitute for
owner-recorded cases in the visual track. They need reuse permission, privacy
screening, timestamp annotations and our own pre-fix/post-fix oracle evidence.
Narration/STT coverage is a separate requirement for the speech track; visual-only
success does not establish it. The 10–20-bug M0 target remains. [INF]

**Execution update (D17).** Docker is the initial backend. M4's SPACE experiment
below is optional; E2B, Daytona or another backend may be evaluated instead when
there is a concrete need. No provider migration is committed. [SRC/INF]

| M | Build | Gate | Est. |
|---|---|---|---|
| **M0** | **Eval set first.** A small web app the owner controls, with 10–20 planted or real bugs. For each bug: a short screen recording with narration (the owner's voice only), annotated with the claim timestamps, the claim text, the commits before and after the fix, and a hand-written reproduction test. Schema in `evals/schema/` | Every reproduction **fails on the pre-fix commit and passes on the post-fix commit** (the oracle/nop check), run and logged | 1 week |
| **M1** | Ingestion + MCP server: transcript + diarization, scene-change frames, screen-region OCR, text embeddings + EmbeddingGemma 2. Tools: `find_moment(query)`, `get_frames(t0, t1)`, `get_transcript(t0, t1)`, `get_screen_text(t)`. Kubrick's pattern with its bugs avoided | Moment retrieval hit@1 and hit@5 within ±5 s on M0, against a Kubrick-style baseline (fixed 45 frames + captions); Wilson CIs | 1–2 weeks |
| **M2** | Claim extraction, plus a codebase checkpoint through the owner's harness via MCP; outputs a list of clarifying questions | Claim precision and recall against the M0 annotations | 1–2 weeks |
| **M3** | **Self-verification.** From clip + claim, the agent writes a reproduction that must fail on the pre-fix commit; then a fix; the reproduction must pass and the regression suite stay green. Docker sandbox. Package each as a Harbor task | Valid-reproduction rate (fails before, passes after) with a Wilson CI; Harbor oracle/nop passes on every generated task | 2 weeks |
| **M4** | Durability + tracing + sandbox: a Temporal workflow per recording (one activity per stage, idempotent); OpenTelemetry traces; proof bundle (clip, frames, trace, Playwright `trace.zip`, test, diff). Behind the `Executor` interface, try **SPACE**: a template per repo/commit, a suspended snapshot of the buggy state restored per attempt, an egress allowlist | Kill the worker mid-run → resume with no duplicated side effects; SPACE and Docker executors give the same M3 results on M0 | 1–2 weeks |
| **M5** | Live input: a Meet/Zoom bot (a hosted meeting-bot API, or a self-hosted Playwright bot with virtual audio) with checkpoints mid-meeting. Try **Scion** for roles (listener / checker / reproducer / verifier) and its chat gateways for "ask me / notify me" | Claim-to-question latency under the owner's threshold on 5 live dry runs | 2 weeks |
| **M6** | Channels: LiveKit SIP + phone; voice as identification plus a second factor (DTMF PIN / app confirm) before any write; optional HUD output. Second applications: the Socratic tutor; health/FHIR (stricter data rules) | A red-team script shows no write action without the second factor | later |

## Not before M3 passes

A SaaS landing page, a `curl | bash` installer, Ray-Ban/HUD clients, multi-tenant Kubernetes, KEDA autoscaling.

## Outputs worth publishing

- **After M0:** the eval-set format and the app, so others can reproduce the setup.
- **After M3:** "Turning bug-walkthrough videos into verified RL tasks", with the reproduction rate and its interval, and the task set on the Hugging Face Hub (no private data).
- **After M4:** a SPACE-executor write-up, if it works, as a possible upstream contribution.
