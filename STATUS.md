# Status

Update this file at every session checkpoint. Read AGENTS.md first.

## Current milestone: M3 (generated self-verification), evaluation in progress

**M0 and M1 have passed; the full MVP is not shipped.** Selected semantic
retrieval, authenticated MCP HTTP and the synthetic audio path work. One-shot
claims failed M2; refined numerical M2 gates now pass under AI-assisted review.
Independent human adjudication remains outstanding. Two distinct generated repairs
have passed unchanged checks, independent regressions and real Harbor nop/oracle
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
   1679 candidate1 now has a full new generated repair/native pass (exec70987
   terminal). Its check covers parallel type transition; the canonical earlier
   exported task also checks sequential mode and XML. Do not mix v1 into v2 scores.
   1623 exhausted both distinct check versions inside candidate1; rejected because
   it explicitly deletes overlays before expecting them to reappear. No repair
   is authorized by that manufactured failure. Exec21395 is terminal.
   1640 exhausted both distinct versions with setup failures (bad relative import,
   then a synthetic popup event missing preventDefault); exec17719 is terminal.
   1638 candidate1 now has an observed generated fail/pass and full independent
   native pass:1772 executed passes, seven skips,1779 discovered. Exec78962 and
   repair67084 are terminal. Its distinct task is exported under
   `tasks/generated-v2/swebench-bpmn-1638`; actual Harbor nop0/oracle1 passes,
   exec9556 terminal. Its report is `notes/runs/harbor-generated-v2-1638.json`.
   No worker is active. Next attempt1610, then the remaining1570/1659/1719/1928 sequentially;
   do not grant extra versions to
   exhausted cases. The five-considered-case report/score is frozen publicly in
   `notes/runs/m3-probed-v2-checkpoint-{report,score}.json`; it does not pass M3.
   The newer six-considered-case snapshot is
   `notes/runs/m3-probed-v2-after-1638-{report,score}.json`:2/11 [5.14%,47.70%],
   five not attempted, acceptance gate still fails. Do not pool v1 and v2.
7. Last read after terminal1638: $3.281019 charged/reserved, $0.718981 available,
   zero pending, cap $4.00. Read `svh budget` again before new work; do not
   raise/reset it. Export each newly verified claim and run actual Harbor
   integrity; preserve the failed v1 results.
8. **Runnable README demo passes:** `.venv/bin/python -I scripts/demo.py` retrieves
   three actual PNG frames via authenticated MCP, then executes Harbor nop0/oracle1
   with frozen generated source/check bytes. The fresh run `readme-e2e-20261021`
   passed primary and varied-ID checks and all1792 executed native tests, seven
   unchanged skips. No model calls. `notes/runs/harbor-readme-e2e-20261021.json`.
   This is recorded-generation replay, not fresh inference or full-MVP completion.
   The README includes setup/output paths; `docs/mvp-usage.md` covers new inputs.
   Latest full harness suite: **105 passed** (including task resume identity and
   ordinary narrated-video transcript flow). No fresh paid speech quality result.
9. Ordinary task narration is now transcribed before extraction, cached privately
   by manifest identity, supplied as quoted timestamped evidence, then reinspected
   via MCP during the code checkpoint. Silent corpus prompts stay unchanged.
   Ordinary visual ingestion is now wired too: `svh ingest --task-manifest ...`
   builds private manifest-bound caption/OCR/transcript caches. `--semantic` adds
   the reviewed local embedding model; default is the explicit lexical baseline.
   Actual ordinary-demo ingestion and all four MCP metadata/frame/search/screen
   tools pass: `notes/runs/ordinary-indexed-mcp-smoke.json`. No new retrieval
   quality claim; M3 all-case gate and independent human adjudication remain open.
10. Ordinary Harbor export now accepts `--task-manifest`, validates the report's
    manifest identity, and uses the already observed native baseline without
    benchmark gold patches. The usage guide includes export/integrity commands.
    Two export tests pass, including ordinary-route gold exclusion and refusing
    an empty/unverified export. `--only` avoids duplicate public claim exports.

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
| M3 generated verification/fix/Harbor | Two distinct claims exported with actual Harbor0/1; v2 2/11 [5.14%,47.70%], five not attempted; finite controls on1679; MVP incomplete |
