# Status

Update this file at every session checkpoint. Read AGENTS.md first.

## Current milestone: M2 (claims and codebase checkpoint), starting

**M0 and M1 have passed; the full MVP is not shipped.** Selected semantic
retrieval, authenticated MCP HTTP and the synthetic audio path work. Generated
claims, reproductions/fixes and Harbor trials have not been measured. [RUN]

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

1. M0 and M1 have passed their measured gates. All visual batches and embedding
   batch exec 38031 are terminal; do not restart them. Selected-method HTTP smoke
   also completed. Full suite: **74 passed**. M1 details and replay commands:
   `notes/2026-10-20-m1-complete.md`; selected report
   `notes/runs/m1-selected-retrieval.json`. Runtime policy selects the measured
   local method; read-only MCP needs no Gemini key.
2. M2 scoring contract is implemented before generation: `evals/m2-rubric.json`,
   `svh.claims.score`, three passing integrity tests; details in
   `notes/2026-10-20-m2-scoring-protocol.md`. Matched M2 extraction is running sequentially in exec session 38364; do not
   restart it while active. Pilot outputs exist in both conditions and remain
   unscored. `notes/2026-10-20-m2-extraction.md`. After completion, freeze and
   review outputs, then run the Docker/MCP code checkpoints.
   Extract claims under matched issue-only/temporal-media conditions, without
   passing gold claims, test names, test/source patches or grader scripts to the
   model. Use the existing deepagents loop for the codebase checkpoint.
3. Docker-only backend and no-delegation harness profile are implemented and
   tested. Actual isolation/transfer/output/timeout/source-fingerprint smoke
   passes; `notes/2026-10-20-docker-harness.md`. No model-generated command has
   executed yet. Use this backend for every code checkpoint/reproduction/fix;
   preserve source fingerprints during read-only M2 inspection.
4. Then measure M2 and proceed to M3 generated reproduction/fix, frozen observed
   fail/pass, independent native regressions, wrong-fix controls and real Harbor
   nop/oracle trials. Preserve prospective gates in `evals/PROTOCOL.md`.

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
| M2 grounded claims/code checkpoint | Not measured |
| M3 generated verification/fix/Harbor | Not measured; MVP incomplete |
