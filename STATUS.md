# Status

Update this file at every session checkpoint. Read AGENTS.md first.

## Current milestone: M3 (generated self-verification), evaluation in progress

**M0 and M1 have passed; the full MVP is not shipped.** Selected semantic
retrieval, authenticated MCP HTTP and the synthetic audio path work. One-shot
claims failed M2; refined numerical M2 gates now pass under AI-assisted review.
Independent human adjudication remains outstanding. One generated repair has
passed unchanged checks, independent regressions and real Harbor nop/oracle
trials. A no-Gemini recording-to-repair replay is runnable from the README. [RUN]

- [RUN] M0 admission: **11/11**, Wilson 95% **[74.12%, 100%]**, meeting the
  10–20-case and lower-bound >=0.70 gate. Proof: `notes/runs/m0-gate.json`.
  Ten GIFs and one silent MOV, all BPMN-js: curated supplied-oracle evidence,
  not speech, model performance or cross-application generalization.
- [RUN] The final replacement, 1928, has now also completed its native oracle:
  pre-fix target assertion fails; post-fix all 1889 executed tests pass with
  unchanged seven skips. The resumed batch (exec session 4399) is terminal.
  It is admitted and included in the frozen eleven-case corpus.
- [CODE/RUN] Admission binds pinned Parquet rows, base commits, source/test patch
  hashes, immutable images, decoded media, manual claim alignment and frozen raw
  log proofs. 1567/1677 fail by runtime exception rather than assertion and stay
  excluded. 1578 passes a supporting invariant but does not directly reproduce
  its broader recorded symptom; archived under `evals/excluded/` (D24).
- [CODE/RUN] `svh freeze-eval` and `load_frozen_corpus` reject incomplete gates,
  overwrites, changed annotations and forged passes on reduced denominators.
  All **54 harness tests pass** under patched pytest 9.1.1. Frozen manifest:
  `evals/frozen-m0.json`; identity `6910fdad889ce36a359981d16ac76c789f5e236eac3556cd3e159112945bad1d`.
- [SRC/INF] First harness selected: deepagents 0.7.28 and official MCP SDK 2.3.0,
  with a thin tool bridge. Released LangChain MCP adapters require MCP <2 and
  are not selected. The selected dependency stack is installed; verify actual HTTP and
  capability interoperability. `notes/2026-10-20-harness-selection.md`, D25.
- [CODE/SRC] Authorized Gemini credentials remain in the external private file
  named by gitignored `.env`; never print or commit keys/screenshots/account IDs.
  Private local API cap is $4.00, below the supplied prepaid balance. Persistent
  `svh.budget` reservations are tested, and a budget-covered model transport is now tested.
  Reasoning and sync/async summarization calls are covered; ambiguous charges
  retain reservations and SDK/middleware retries are disabled. `notes/2026-10-20-gemini-access.md`.
- [RUN/SRC] Host and fixture sandbox use pytest 9.1.1 after three GitHub alerts
  for CVE-2025-71176. All three original frozen fixture checks still fail before
  and pass after: 3/3, Wilson 95% [43.85%, 100%]. New proof:
  `notes/runs/fixture-oracle-pytest9.json`; default image promoted after checks.
  Remote alert closure was still pending at last read. Details in
  `notes/2026-10-20-pytest-upgrade.md`.
- [SRC/INF] Owner-requested side-agent literature review is completed and pushed:
  `docs/literature-review.md`. GUIRepair, ViBR, Framesleuth, direct Multimodal
  successors and CoHarden inform design; no external system was executed.
- [INF] M1–M3 prospective acceptance and shipping evidence are fixed before model
  measurements in `evals/PROTOCOL.md` (D26). Reference projects, embedders and
  storage choices are replaceable. Docker is current; no cloud migration needed.
- [RUN] M1 selected local text-only EmbeddingGemma 2 retrieval passes, with
  observation-focused queries over unchanged 45-frame captions. Earlier lexical
  and raw semantic failures are preserved; all are development-set measurements.
  Strict @1 is 4/11 [15.17%,64.62%]; no unseen-app or speech quality claim.
  `notes/2026-10-20-m1-complete.md`. Total cost **$0.464144** across 19 settled
  Gemini requests, no unsettled reservations; **$3.535856** local budget remains.
- [CODE/RUN] MCP HTTP boundary now works with the frozen corpus: authenticated
  loopback access, registered metadata, bounded PNG frames, silent-media status,
  resources and a versioned prompt. Actual SDK protocol: 2026-07-28. Thin tool
  bridge preserves structured/image evidence; deepagents tool flow tested with a
  deterministic test model. Actual CLI smoke on public video passed:
  `notes/runs/mcp-http-smoke.json`. All **57 tests pass**, including auth/origin,
  trusted-input and image-bridge checks. `notes/2026-10-20-mcp-boundary.md`.

## Next concrete steps

1. M0/M1 passed. M2 sequential exec93013 is terminal: all eleven cases in both
   conditions completed with source unchanged. Refined media grounded precision
   and recall: **10/11 [62.26%,98.38%]**; issue-only content **9/11
   [52.30%,94.86%]**. Numerical gate passes, but the protocol's independent human
   scoring remains outstanding: judgments are explicitly AI-assisted.
   `notes/2026-10-21-m2-refined-results.md` contains exact artifact pointers.
2. Build M3's prospective measurement before its features. Generate checks on
   buggy source, freeze and observe assertion failure, then generate source-only
   fixes, rerun unchanged checks and independent native regressions. Attempt all
   eleven, retain budget exhaustion. Use Docker and the existing deepagents loop.
3. Normal task input must work without supplied gold fixes/tests or prior corpus
   admission; see `notes/2026-10-21-mvp-completion-audit.md`. Export every fully
   verified claim and execute actual Harbor nop/oracle trials. MVP is incomplete.
4. **First full generated repair passes (1679 candidate2).** Original generated
   Chrome check fails at the actual XML assertions, unchanged check passes after
   generated source fix; independent native suite: 1792 pass, seven unchanged
   skips, 1799 discovered. Finite wrong-fix controls expose a fixture shortcut;
   a separately observed fail/pass ID variation now guards the Harbor task.
   `notes/2026-10-21-first-generated-repair.md` and task proof contain evidence.
5. Actual Harbor integrity passes for the exported1679 task: nop reward0,
   oracle reward1, primary/independent browser checks and native suite observed.
   All old workers are terminal. First v1 run remains incomplete: one verified
   repair, seven considered cases including 1557 abstention, four unattempted.
6. Reproduction development now has controller-owned browser probes inside the
   existing SDK loop, actual MCP images delivered before inference, two distinct
   check versions per case and frozen probe references. Targeted integrity checks
   pass; `notes/2026-10-21-m3-browser-development.md` describes the measured limits.
   A fresh **probed-v2** all-eleven run uses unchanged rubric, Lite/low. Its1557
   ambiguity is an abstention;1655 exhausted two checks, both explicitly rejected
   for wrong DI-property assertions (the second also expected the wrong color).
   1679 candidate1 has a reviewed target type-transition failure; repair/native
   stage is running in exec70987. Do not mix the earlier v1 success into v2 scores.
7. Last read before the v2 repair: $3.208077 charged/reserved, $0.791923 available,
   zero pending, cap $4.00. Read `svh budget` again after terminal repair; do not
   raise/reset it. Export each newly verified claim and run actual Harbor
   integrity; preserve the failed v1 results.
8. **Runnable README demo passes:** `.venv/bin/python -I scripts/demo.py` retrieves
   three actual PNG frames via authenticated MCP, then executes Harbor nop0/oracle1
   with frozen generated source/check bytes. The fresh run `readme-e2e-20261021`
   passed primary and varied-ID checks and all1792 executed native tests, seven
   unchanged skips. No model calls. `notes/runs/harbor-readme-e2e-20261021.json`.
   This is recorded-generation replay, not fresh inference or full-MVP completion.
   The README includes setup/output paths; `docs/mvp-usage.md` covers new inputs.
   Latest full harness suite: **100 passed** (including task resume identity).

## Evidence and history

- Original intent: `docs/idea/` (never edit); analysis/roadmap/decisions/references:
  `docs/`. Source release and audit: `notes/2026-10-20-swebench-multimodal-pilot.md`.
- Native execution reports: `notes/runs/native/`; admitted immutable proof
  metadata: `notes/runs/proofs/`; raw media/rows/logs/gold patches stay ignored in
  `data/external/`. Manual reviews: `evals/reviews.json`.
- Reproduction, resume and fresh-clone commands:
  `notes/2026-10-20-external-admission.md`. The pilot log-path resume bug is fixed
  and its report now regrades correctly; historical proof snapshots are intact.
- Earlier bootstrap/fixture work: `notes/2026-10-20-m0-checkpoint.md`, fixture
  app commits `426a532` and `eee15eb`. Fixture-only success did not pass M0.

## Gates

| Gate | Current evidence |
|---|---|
| M0 visual supplied-oracle corpus | Passed: 11/11, Wilson 95% [74.12%, 100%]; frozen manifest saved |
| M1 ingestion/retrieval/MCP | Passed: selected hit@1 9/11 [52.30%,94.86%], hit@5 11/11 [74.12%,100%]; weak strict localization; audio functional/MCP smoke pass |
| M2 grounded claims/code checkpoint | Refined numerical gate passed: 10/11 [62.26%,98.38%]; all source unchanged; independent human scoring outstanding |
| M3 generated verification/fix/Harbor | First generated repair + native regressions + finite controls + actual Harbor trials pass; v1 1/11 [1.62%,37.74%] partial checkpoint; v2 evaluation active; MVP incomplete |
