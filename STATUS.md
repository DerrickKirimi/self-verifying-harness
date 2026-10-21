# Status

Update this file at every session checkpoint. Read AGENTS.md first.

## Current milestone: numerical M3 passed; independent human review outstanding

**M0 and M1 have passed; the full MVP is not shipped.** Selected semantic
retrieval, authenticated MCP HTTP and the synthetic audio path work. One-shot
claims failed M2; refined numerical M2 gates now pass under AI-assisted review.
Independent human adjudication remains outstanding. The completed, explicitly
financially amended eleven-case v5 run passes numerical M3:5/11 valid pairs
[21.27%,71.99%],4/11 full native-passing repairs [15.17%,64.62%],zero pending.
Four distinct generated repairs
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
  Initial local API cap was $4.00; the owner's explicit additional funding now
  authorizes a cumulative $12.195678 (latest explicit five-dollar allowance;
  see entry20). Persistent
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

## Next concrete step

**Complete the independent human review described in `docs/independent-review.md`.**
Both frozen media-grounded and issue-only packets are ready; no paid model call
is needed for that review. Do not claim independent judgments or full MVP shipping
until a real reviewer supplies them. All inference/Harbor workers are terminal.
The README demo is runnable; all148 harness tests pass. The completed v5 run is
historical and frozen; release adapter changes after it intentionally prevent
resuming it under mismatched source hashes. Any further evaluation needs a new
prospectively pinned method, not extra versions in exhausted cases.

The numbered entries below preserve chronological implementation history; entry21
is the latest measured checkpoint.

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
   1610 now exhausted both versions: its check resets the current root to itself,
   never switching planes, so alignment is explicitly rejected and no repair is
   authorized. Exec42122 is terminal. Remaining public cases:1570/1659/1719/1928.
   Ordinary synthetic audio v1 omitted transcript reinspection and v2 exceeded
   graph steps during unbounded source reads; both fail before reproduction and
   remain retained. A documented fixture-author clarification and bounded SDK
   checkpoint now let `ordinary-audio-v3` complete extraction/code review and
   observe its generated target assertion fail. Repair/native now pass, exec52652
   terminal:1772 executed native passes, seven skips, same1779 coverage as the
   independently observed original native baseline, without benchmark gold.
   Ordinary private export and actual Harbor nop0/oracle1 now pass; exec68550 and
   Harbor44084 terminal. `notes/runs/harbor-ordinary-audio-v3.json` pins its bundle.
   Its outcome stays outside the public denominator. Public1719,1928,1570 and1659
   are now terminal, exhausting their two distinct versions. All11 public cases
   are considered; final v2 score is2/11 [5.14%,47.70%],zero pending,gate fails.
   See `notes/2026-10-21-m3-probed-v2-results.md` and final report/score snapshots.
   A fresh mapped-flex-v3 method is now frozen with relocated-import examples,
   recorded-transition fidelity and Lite/Flex/medium. Its1640 candidate2 reproduces
   the actual subprocess transition and loses loop cardinality after initial-state
   assertions pass; repair36204 is terminal, returning an empty edit list and
   failing validation. Candidate1 is rejected
   because it substituted a Task for the reported SubProcess. Continue sequentially,
   without pooling v1/v2 results. Case1570 candidate1 is terminal (exec64346):
   rejected because whole-viewbox equality can fail on legitimate content-bound
   changes. Candidate2 was not executed: automatic approval review reached its
   service usage limit. The owner confirmed capacity restored; that exact second
   candidate command was approved and completed (exec29006): its viewport x/y
   assertions pass on buggy code, then an additional probe is refused by the
   case-wide version limit. Case1610 fails on a provider ServerError (exec64778),
   retaining the full $0.167527 reservation. Case1623 (exec71506) is terminal with
   BudgetExceeded before any provider request. All seven remaining cases are now
   terminal with the same actual local refusal; no paid requests were dispatched.
   Final v3 has0/11 generated fail/pass pairs [0%,25.88%], no pending stages and
   no active worker. It fails the gate and is budget-limited, not a clean method
   comparison. See `notes/2026-10-21-m3-mapped-flex-v3-results.md`. Prior stopped
   evidence is retained in `notes/2026-10-21-m3-mapped-flex-v3-checkpoint.md`;
   do not grant extra versions to
   exhausted cases. The five-considered-case report/score is frozen publicly in
   `notes/runs/m3-probed-v2-checkpoint-{report,score}.json`; it does not pass M3.
   The newer six-considered-case snapshot is
   `notes/runs/m3-probed-v2-after-1638-{report,score}.json`:2/11 [5.14%,47.70%],
   five not attempted, acceptance gate still fails. Do not pool v1 and v2.
7. The owner has now explicitly funded further work: reported balance$11.51,
   monthly usage/limit$2.69/$12, auto-renew off. A recorded funding event raises
   the cumulative local cap from$4 to$12 without resetting charges or releasing
   the$0.167527 uncertain reservation. At authorization: charged/reserved$3.861395,
   available$8.138605, settled estimate$3.693868. Read `svh budget` again before
   work; retain this historical funding event. A later explicit five-dollar
   allowance is recorded in step20; do not reset charges. `notes/2026-10-21-funding-authorization.md`.
   Export each newly verified claim and run actual Harbor
   integrity; preserve the failed v1 results.
8. **Runnable README demo passes:** `.venv/bin/python -I scripts/demo.py` retrieves
   three actual PNG frames via authenticated MCP, then executes Harbor nop0/oracle1
   with frozen generated source/check bytes. The fresh run `readme-e2e-20261021`
   passed primary and varied-ID checks and all1792 executed native tests, seven
   unchanged skips. No model calls. `notes/runs/harbor-readme-e2e-20261021.json`.
   This is recorded-generation replay, not fresh inference or full-MVP completion.
   The README includes setup/output paths; `docs/mvp-usage.md` covers new inputs.
   Previous full harness suite: **116 passed** (including task resume identity and
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
11. Audio-only `.wav` input is now supported through normal registration,
    bounded transcription, lexical transcript search, spoken-claim extraction,
    mandatory transcript reinspection and transcript-only generation context.
    Frame/screen tools return explicit `no_video`; no invented frames. Actual
    provider + all-five-tool MCP smoke passes on9.36s synthetic narration:
    `notes/runs/audio-only-provider-mcp-smoke.json`. No human speech-quality claim.
12. Ordinary audio checkpoints now force actual metadata/transcript replies and
    bounded source inspection inside the existing SDK loop. Explicit resumes
    retain separate attempt traces, preparation errors retain phase/budget, and
    cached successful checkpoints are hash-bound. See
    `notes/2026-10-21-ordinary-checkpoint-controls.md` and the retained failure
    report. The garbled original audio is not silently corrected or counted as
    accurate transcription; v3 uses an explicit text clarification.
13. Unclear extraction now prints its questions and abstains before Docker/code
    inspection. A long-recording sampler bug is fixed: the fixed45 grid now uses
    centered windows <=30s even for the advertised one-hour input bound. Ten
    targeted ingestion/preparation tests pass; no long-meeting quality claim.
14. Trusted Chrome discovery is fixed for newer Puppeteer configs, setting the
    installed executable before loading upstream Karma. Exact1928 frozen checks
    reexecuted after that fix still fail on bad imports; no new version granted.
    An older image's exact frozen check/fix retains actual fail/pass under the new
    runner. Both reports are in `notes/runs/`. Existing bundles remain unchanged.
15. Reviewed Flex transport now passes an actual access smoke and reserves the
    full authenticated input limit plus maximum output at matching reviewed rates.
    No retries, Standard fallback or cap change. Root-spec reference imports are
    mapped to project-root aliases with original hashes; model checks are never
    rewritten. New method/source hashes are frozen before v3 calls. See
    `notes/2026-10-21-next-evaluation-budget-options.md`.
    Full harness suite: **123 passed**, with one expected SDK warning from the
    test that rejects an invalid `auto` tier. No model calls in this test suite.
16. Fresh **content-flash-flex-v4** is frozen before its calls: stronger
    Gemini3.8Flash/Flex/medium, actual MCP frames, root-mapped spec examples,
    grep forced to return content, five repair reads and nonempty typed edits.
    Same eleven cases/rubric/two distinct test versions, no pooled successes.
    Case1640 candidate1 is terminal (exec50848): it spends both versions on a
    passing fixture smoke and assertion-free DOM inspection, so no target failure
    qualifies and no extra version is granted. Case1638 candidate1 is terminal
    (exec42464): its actual probe reaches the target null-versus-undefined DI
    assertion, but the final model call fails with recorded HTTP503. No successful
    stage is fabricated. Candidate2 (exec65843) now completes and observes both
    empty-string/null cases fail at DI-label removal after initial and rendered
    assertions pass. Its exact frozen check is explicitly aligned; repair is
    repair94405 is now terminal with HTTP503, no generated fix. No third distinct
    version was granted. V4 is preserved incomplete (3/11 considered,8 unattempted),
    with no generated pair; see `notes/2026-10-21-flash-flex-checkpoint.md`.
    Last ledger afterv4: charged/reserved$4.958983, available$7.041017, three
    unsettled requests ($0.984679). New source/funding/privacy tests
    pass: **128 total**, one expected invalid-tier warning. Error records now
    preserve valid integer HTTP status without provider error/request text;
    old1610 status remains unknown. Local Ollama tag deepseek-r1:8b reports only
    completion/thinking, no tools/vision; it was inspected but not used as a
    substitute. No model download or local inference was performed.
17. Independent human review now has a concrete handoff:
    `docs/independent-review.md`, `evals/m2-human-review-template.json` and a
    separate `evals/m2-human-issue-only-template.json` for the paired baseline.
    All eleven existing contact-sheet hashes were checked against actual PNGs;
    the blank template binds the exact refined output hash and deliberately has
    null decisions, which the actual scorer rejects. No previous AI decisions
    or reasons are copied. This prepares the outstanding review; it does not
    claim that a human has reviewed or passed it.
18. Fresh **standard-submission-v5** is frozen before calls: Gemini3.8Flash/
    Standard/medium, same11 cases and rubric, no copied successes. The internal
    tool is now `submit_browser_reproduction` and explicitly requires the reported
    action and corrective assertions on the first version; the read-budget
    checkpoint repeats that contract. Execution/version limits are unchanged.
    Standard is an explicit new-run selection after Flex capacity errors, not
    automatic fallback. All128 harness tests still pass. Case1640 candidate1
    reproduction65942 is terminal: initial markers/properties and actual popup
    transition pass, then cardinality preservation fails on the real SubProcess.
    Exact frozen check is explicitly aligned; repair88697 completes with unchanged
    check pass and1776 executed native passes, seven unchanged skips (1783 total).
    Finite controls50086 pass: deletion/suppression rejected by assertions; a
    recorded-ID shortcut passes primary but fails the independent changed-ID/
    cardinality/condition check. That independent check itself fails on base and
    passes unchanged after the generated fix. Export80790 is terminal:
    `tasks/generated-v5/swebench-bpmn-1640`; actual Harbor21376 now completes
    nop0/oracle1, primary/variation/native all pass. Bundle remains immutable.
    Checkpoint score1/11 [1.62%,37.74%], two considered/nine unattempted, still no
    gate pass. Last read after repair: charged/reserved$5.234003,
    available$6.765997, three unsettled reservations retained. Inspect actual
    `notes/2026-10-21-subprocess-generated-repair.md` records the complete unit.
    Commit e9a98a4 is pushed. Case1638 candidate1 reproduction73848 is terminal:
    both actual label paths fail on null-versus-undefined after valid initial
    state/actions. Exact frozen check is aligned; repair20871 is terminal with
    ValueError: the model used an absolute SourceEdit path, rejected before any
    patch was applied. Case1638 candidate2 reproduction29190 is terminal with
    both target assertions after additional rendered-state checks. Its exact
    frozen check is aligned; candidate2 repair77011 now completes actual unchanged
    check pass and1772 native passes/seven unchanged skips (1779 discovered). No
    model output is manually corrected. See the captured format gap in
    `notes/2026-10-21-source-edit-format-gap.md`; fix after the pinned run.
    Its model source file is byte-identical to the existing canonical1638 task,
    whose actual Harbor0/1 remains linked; no duplicate claim/task is exported.
    Fresh v5 score2/11 [5.14%,47.70%], three considered/eight unattempted, still
    no gate pass. Case1679 candidate1 (exec2864) is terminal without a generated
    check: final response MAX_TOKENS,7864 output tokens all reported as reasoning,
    no tool call/code and no executed check versions. Candidate2 (exec13546)
    completes a check. An initial rejection based on raw-source stack offsets is
    corrected after actual CDP source capture: compiled lines75/106 are the wrong
    loop-type assertions, after popup selections pass. Original review and failed
    diagnostics are preserved; no generated test is changed or added. The exact
    frozen check is aligned and repair is now running. See
    `notes/runs/m3-standard-submission-v5-1679-stack-review.json`.
    Case1655 candidate1 (exec22822) is terminal: MAX_TOKENS,7863
    output tokens all reported as reasoning, no code or executed check. Its
    candidate2 (exec29053) is terminal with assertions but explicitly rejected:
    it reuses text nodes captured before setColor and observes empty computed
    style rather than the recorded wrong fill color, without establishing a
    current connected node. No source fix or third candidate is authorized.
    Case1610 candidate1 (exec99230) now has two actual post-navigation editor
    failures after valid active/attached initial state; its exact check is
    aligned; repair61864 passes its generated check but fails a held-out native
    regression because cancellation loses an unsaved edit. The source fix is not
    fully verified and is not exported. Do not feed held-out test details to the
    next generation model. The1679 repair12249 now passes its exact check and1792
    native tests/seven unchanged skips (1799 discovered). Its source bytes equal
    the existing canonical task; no duplicate is exported. Fresh v5 checkpoint:
    4/11 valid pairs [15.17%,64.62%],3/11 full repairs [9.75%,56.56%], six
    considered/five unattempted, gate not yet passed. Case1928 reproduction72501
    now observes actual space-tool drag resize an empty pool from60 to160; its
    repair44724 now completes unchanged check pass and1889 native passes/seven
    unchanged skips (1896 discovered). Export18747 is terminal:
    `tasks/generated-v5/swebench-bpmn-1928`; actual Harbor36819 now completes
    nop0/oracle1 with primary/native integrity. Its bundle remains immutable.
    Fresh checkpoint5/11 valid pairs [21.27%,71.99%],4/11 full repairs
    [15.17%,64.62%],seven considered/four unattempted. The gate still refuses
    completion until every frozen case is considered. Last read after repair:
    charged/reserved$7.021649, available$4.978351, three
    uncertain reservations retained.
    Commit193499b is pushed. Remaining cases1570/1623/1659/1719; case1570
    candidate1 (exec71008) is terminal after one base-passing viewport check and
    no trusted target failure. Its candidate2 did not launch before access-policy
    expiry; no second candidate directory or new charge was produced then.
    Renewal and the explicitly recorded financial amendment now permit resumption,
    with one additional distinct executed version available. Do not stop on the positive interval;
    finish the frozen denominator and resolve release audit items.
19. Release audit found no supported later-day model-policy renewal: the probe
    writes a current access timestamp but a hardcoded old pricing date, and the
    factory rejects that mismatch/age. Current metadata expires at18:22UTC today.
    The expiry checkpoint is frozen before maintenance. The supported renewal
    is now implemented and actually tested; see step20. README replay is unaffected.

20. The owner explicitly authorized up to **$5 additional usage**. At the actual
    checkpoint charged/reserved was$7.195678; cumulative local cap is now
    **$12.195678**, allowing exactly$5 more, preserving all three unknown
    reservations. No provider billing setting is changed. Authorization:
    `notes/2026-10-21-additional-five-dollar-authorization.md`.
    Supported renewal independently expires price/access reviews, binds exact
    price-policy bytes, preserves old evidence and refuses partial failures.
    Actual authenticated metadata refreshed19:43UTC; all four model/tier factory
    constructions pass without generation or ledger changes. All **146 tests
    pass** with loopback networking (one expected invalid-tier warning).
    `notes/2026-10-21-model-policy-renewal.md` and usage guide explain renewal.
    Before any resumed paid call, an explicit financial amendment was frozen:
    `evals/m3-method-standard-submission-v5-renewed.json`, SHA
    `0549beafdb54056c923e24b76bac9ad66adc6c4b9e50074c4cd464b3ef1db0ea`.
    Original method and exact expiry report/score remain retained; the amended
    development run has two financial epochs, unchanged generation method/rates/
    limits and no extra candidate versions or pooled successes from other runs.
    The permitted1570 candidate2 has now been launched after renewal. Finish
    that case and1623/1659/1719 sequentially, then measure the entire denominator.

21. **All eleven cases now considered; numerical M3 passes**, with zero pending
    stages. Valid pairs5/11 [21.27%,71.99%], full native-passing repairs4/11
    [15.17%,64.62%]. The disclosure and exact final report/score are linked from
    `notes/2026-10-21-m3-standard-submission-v5-results.md`. No earlier run's
    successes are pooled. Cases1570/1623/1659/1719 add no verified repair; their
    errors, invalid assertions and one mistaken controller launch cancelled before
    generation are retained in `notes/2026-10-21-v5-resumed-failures.md`.
    The source-path ambiguity is now fixed after evaluation: only canonical
    `/workspace/lib/...js` is normalized, with original traversal/extension and
    exact replacement checks. Actual captured1638 output replays in Docker:
    original frozen check fails before, passes after;1772 native passes/seven
    skips. Source bytes match the separately verified candidate2. This is an
    interface replay, not a retroactive score change or new exported claim:
    `notes/runs/source-path-alias-replay.json`. New candidate preflight now refuses
    exhausted distinct-version capacity before model/MCP setup. All **148 tests
    pass**, one expected invalid-tier warning. No paid call for release checks.
    Final charged/reserved **$8.454073**, cap **$12.195678**, available
    **$3.741605**, three uncertain reservations retained. Since the owner's latest
    authorization, actual increase is **$1.258395 of the $5 allowance**. No model
    worker remains. README and usage instructions are current. Independent human
    adjudication remains the unresolved protocol requirement; full MVP shipping
    is not claimed.

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
| M3 generated verification/fix/Harbor | Numerical gate passed in explicitly financially amended v5: all11 considered,zero pending;5/11 valid pairs [21.27%,71.99%],4/11 full repairs [15.17%,64.62%]; four distinct public tasks plus ordinary audio have actual Harbor0/1; human adjudication outstanding |
