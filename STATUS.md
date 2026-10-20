# Status

Update this file at every session checkpoint. Read AGENTS.md first.

## Current milestone: M1 (ingestion and MCP), starting

**M0 has passed; the full MVP is not shipped.** MCP HTTP evidence access works.
Paid visual ingestion and synthetic audio smoke are complete. The lexical
retrieval comparison failed M1; generated reproductions/fixes and Harbor trials
have not been measured. [RUN]

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
- [CODE/RUN] MCP HTTP boundary now works with the frozen corpus: authenticated
  loopback access, registered metadata, bounded PNG frames, silent-media status,
  resources and a versioned prompt. Actual SDK protocol: 2026-07-28. Thin tool
  bridge preserves structured/image evidence; deepagents tool flow tested with a
  deterministic test model. Actual CLI smoke on public video passed:
  `notes/runs/mcp-http-smoke.json`. All **57 tests pass**, including auth/origin,
  trusted-input and image-bridge checks. `notes/2026-10-20-mcp-boundary.md`.

## Next concrete steps

1. Curation is complete and frozen. Do not restart either terminal Docker batch.
   M0 now passes on all eleven admitted cases; use the frozen manifest in M1.
2. Budget-covered Gemini transport is tested, including actual summarization
   middleware and all public call modes. Authenticated metadata confirms both
   candidate models and token limits. Eleven transport tests pass; full suite
   now 72 passed including visual timeline/retrieval/audio and HTTP checks. See `notes/2026-10-20-budgeted-gemini.md`.
   Disable delegation through the selected harness profile and verify Docker
   boundaries before executing any generated code.
3. Visual ingestion batch 6879 is terminal: all eleven corrected 45-frame indexes
   exist. Do not restart it. The lexical baseline fails M1 (hit@1 8/11, hit@5
   9/11); temporal windows fail too. Frozen reports:
   `notes/runs/m1-lexical-baseline.json`, `notes/runs/m1-retrieval.json`.
   Audio functional and updated actual MCP smoke pass. Total settled cost
   $0.464144 including abandoned runs; no unsettled requests at this checkpoint.
   See `notes/2026-10-20-m1-ingestion-design.md`.
4. Evaluate pinned local EmbeddingGemma 2 text-only semantic retrieval on the
   unchanged captions, preserving the failed lexical baseline and fixed gate.
   CPU-only optional dependencies and safe-weight downloads are being prepared;
   no semantic inference or improvement has been measured yet. M2/M3 features
   wait for M1: then claims/checkpoints, generated check/fix, held-out regressions,
   wrong-fix controls and actual Harbor oracle/nop trials.

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
| M1 ingestion/retrieval/MCP | Lexical retrieval gate failed; audio functional and MCP smoke passed |
| M2 grounded claims/code checkpoint | Not measured |
| M3 generated verification/fix/Harbor | Not measured; MVP incomplete |
