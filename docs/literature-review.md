# Related work: recordings, software repair and self-verification

Reviewed **2026-10-20**. Ordered by relevance to this project's intended
recording → claim → executable reproduction → fix → verification workflow,
rather than citation count or leaderboard position. [INF]

**The closest precedents already combine visual reports, reproduction code and
browser feedback.** GUIRepair is a direct repair predecessor; ViBR directly
replays recorded bugs; Framesleuth overlaps the recording-to-MCP interface.
Our proposed distinction is the combination of timestamp-grounded claims,
mandatory executable evidence, an independent evaluation boundary and reusable
Harbor tasks, eventually during meetings. This is a positioning hypothesis,
not a claim that nobody has built the combination. [INF]

**The main caution is oracle strength:** a frozen failing test prevents some
forms of self-confirmation, but it can still accept an incorrect fix.
CoHarden studies this failure explicitly. [SRC]

This is a focused review, not an exhaustive systematic literature review.
The entries state the inspection scope: paper sections, project documentation
or repository README. **No paper is represented as read cover-to-cover** and
none of the external systems was executed in this review. [RUN] Paper model
names and experiments are historical observations, not current deployment
recommendations. Scores are deliberately omitted: this repo has not rerun a
common model/budget/task-release comparison. Older SWE-bench M results are not
automatically comparable with the refreshed release we use. [INF]

## 1. GUIRepair — the closest visual repair workflow

Huang et al., *Seeing is Fixing* (2025).
[Paper v1](https://arxiv.org/html/2506.16136v1),
[author project](https://sites.google.com/view/guirepair).
Read: motivation, method §III, evaluation setup and project reproduction notes.

- [SRC] Uses **SWE-bench Multimodal**. Image2Code retrieves project documentation
  and generates runnable code for the reported visual scenario. Code2Image
  renders candidate patches and asks a model to select a promising repair from
  their visual effects.
- [SRC] §III-D describes **manual runtime/project setup and package import**
  for browser reproduction. Patch selection uses rendered feedback rather than
  a newly generated executable assertion. The historical project instructions
  require the then-closed `sb-cli` evaluation route.
- [INF] Borrow documentation-grounded reproduction and browser evidence.
  Account for setup labor; do not equate a model's visual approval with an
  assertion proven failing before the patch. Our pipeline should automate or
  explicitly record setup rather than hide it in curation.

## 2. ViBR — direct replay from bug videos

Feng et al., *ViBR: Automated Bug Replay from Video-based Reports using
Vision-Language Models* (FSE 2026).
[Paper v1](https://arxiv.org/html/2604.19905v1).
Read: method §2, replay evaluation §3.3, threats/data-availability sections.

- [SRC] Android recordings are segmented using consecutive-frame CLIP
  similarity; pre-action/post-action frames and a region of interest guide
  comparison with the live GUI. It can explore to restore a missing
  precondition, then infer tap/scroll/input actions. Runtime perception combines
  screenshots and UIAutomator metadata.
- [SRC] Replay evaluation uses **44 recordings**, selected after checking
  historical-version availability, credentials and visible symptoms. Success
  means reaching the recorded buggy state; this is not a source-repair benchmark
  or a pre/post-fix test-generation evaluation.
- [INF] Treat action segmentation, state alignment and assertion synthesis as
  different problems. A screenshot sequence can guide reproduction without
  supplying the expected behavior. Browser DOM/accessibility data can play the
  runtime-grounding role, while a saved recording itself lacks that metadata.
  This is adjacent Android evidence, not measured browser transfer.

## 3. CoHarden — the most important warning about “self-verification”

Tan et al., *Beyond Fail-to-Pass: Iterative Hardening of Co-Generated Bug
Reproduction Tests and Fixes* (July 2026 preprint).
[Paper v1](https://arxiv.org/html/2607.19843v1).
Read: empirical study §2, method §3, discussion and implementation notes.

- [SRC] Distinguishes **rigorous**, **lax** and **misaligned** reproduction
  tests. Lax tests fail on buggy code and pass on the gold fix, yet also accept
  plausible wrong fixes. Co-generated tests and fixes can share a mistaken
  interpretation. The study uses the SWE-bench/SWT-bench setting, not the
  Multimodal benchmark.
- [SRC] Mutation Patch Evaluation compares generated and reference tests on
  fix variants. CoHarden begins with a test before source edits, then hardens
  test/fix pairs using mutants. Its live loop uses the previous test as a
  surrogate reference; it does not have an independent gold oracle there.
- [INF] Keep our fail-before rule. Add challenges that suppress symptoms,
  hardcode the visible example or remove the feature, and check whether the
  verifier rejects them. Surviving a finite mutant set still does not establish
  complete correctness; a moving reference can also preserve a shared mistake.

## 4. VisualRepair — GIF handling and targeted visual inspection

Xiao et al., *Dynamic Tool Calling and Region Focusing for Visual Software
Issue Repair* (July 2026 preprint).
[Paper v1](https://arxiv.org/html/2607.14075v1).
Read: tools/localization/selection §III, setup §IV and parameter studies.

- [SRC] Builds directly on **SWE-bench Multimodal's older 517-test/102-dev
  split**. Routes GIFs through keyframe extraction, distinguishes text/code/UI
  inputs, and generates repository-level reproduction templates. Region
  grounding plus zoomed views diversifies candidate patches.
- [SRC] Selection filters compile failures and, for supported templates,
  renders screenshots. Identical-to-buggy output is rejected; a model then
  judges remaining visual results.
- [INF] Useful hypotheses for M1: preserve temporal context, request a crop
  on demand, and retain the wider frame. Pixel change alone is weak evidence:
  changing a color or blanking the page can differ from the bug without fixing
  it. Template coverage and extra candidate calls belong in cost accounting.
  Its claim that suffix-based GIF routing has no error should not replace
  decoded media-type validation in our harness.

## 5. FailureMem — reusable failure experience without gold leakage

Ma et al., *A Failure-Aware Multimodal Framework for Autonomous Software
Repair* (March 2026 preprint).
[Paper v1](https://arxiv.org/html/2603.17826v1).
Read: method §3, evaluation setup, memory-construction appendix A and visual tools.

- [SRC] Evaluates on **SWE-bench Multimodal**. Combines structured localization
  with flexible repair exploration, crop/grounding tools and a hierarchical
  failure memory. Entries store symptoms, negative constraints, general repair
  principles and failed-versus-gold patch summaries.
- [SRC] Appendix A says the memory comes from development-set failures;
  developer gold patches participate in offline distillation. Memory retrieval
  therefore differs from learning only from an agent's own observed outcomes.
- [INF] Save failed attempts and reasons, but isolate evaluation gold fixes
  and their derivatives from the agent's retrieval store. Split by issue and,
  where possible, repository/time; abstract prose can still leak a solution.
  A memory mechanism is optional until a no-memory baseline demonstrates a need.

## 6. SWE-bench Multimodal / SWE-agent M — foundation and release discipline

Yang et al. (ICLR 2025).
[Original paper v1](https://arxiv.org/html/2410.03859v1),
[official release page](https://www.swebench.com/multimodal.html).
Read: collection/features §2, adaptations §3, analysis §4 and v2 announcement.

- [SRC] Task resolution requires supplied fail-to-pass and pass-to-pass tests.
  SWE-agent M adds browser, screenshot and image-viewing actions. Visual inputs
  include screenshots, actual/expected pairs and temporal media; the benchmark
  is broader than narrated bug recordings.
- [SRC] The official **2026-09-01 v2** announcement describes rebuilt evaluation
  environments/grading and **480 test tasks** selected for reproducibility.
  Original-paper counts and results describe a different release.
- [RUN] This repo separately audited pinned files and temporal candidates:
  [local audit](../notes/2026-10-20-swebench-multimodal-pilot.md).
- [INF] A useful source corpus does not automatically validate our claim
  extractor, generated reproduction or speech path. Compare identical task
  revisions and isolate supplied tests/gold patches from agent-visible context.
  Preserve native grading as independent evidence, not as training input.

## 7. OpenHands-Versa — a practical existing-harness baseline

Soni et al., *Coding Agents with Multimodal Browsing are Generalist Problem
Solvers* (2025; EACL Findings 2026).
[Paper v1](https://arxiv.org/html/2506.03011v1),
[reference repo](https://github.com/adityasoni9998/OpenHands-Versa).
Read: tools, evaluation setup, tool-use analysis and failure discussion; README.

- [SRC] Evaluates on **SWE-bench Multimodal**, GAIA and The Agent Company with
  an existing coding agent plus visual browsing, file access and search.
  The same-backbone comparison retains similar SWE-bench M performance;
  headline cross-system gains also involve different underlying models.
- [SRC] Failure analysis explicitly includes incomplete tests, premature
  stopping and omitted repository regression checks. The README recommends
  upstream OpenHands for using the method rather than the experiment fork.
- [INF] Supports our choice to expose tools to an existing coding harness.
  Browser availability does not enforce verification: enforce evidence and
  stage transitions outside the model's voluntary workflow. Use matched model,
  budget and information access when comparing harnesses.

## 8. Framesleuth — the closest recording-to-MCP product neighbor

[Author repository](https://github.com/thestackhub1/framesleuth-agent).
Read: README architecture, Context Bundle, grounding, quality and evaluation
descriptions. **Repository documentation only; implementation and execution
not audited.** Web branch is mutable, not a pinned dependency.

- [SRC] Describes local recording analysis with transcription, keyframes,
  visual understanding, optional browser sidecars, workspace grounding and
  evidence-linked Context Bundles exposed over MCP/HTTP. Scope includes bugs,
  features and design walkthroughs. Capture is outside the analysis repository.
- [INF] This is substantial interface overlap; we should not claim novelty
  for “video to coding-agent context over MCP.” Documentation about bundle
  faithfulness or citation resolution does not establish code-level fail/pass
  oracles. A stronger end-to-end claim would require inspecting/running that
  path, which this review did not do. Borrow ideas about thin-evidence reporting
  and sidecar provenance without adopting its models or dependencies by default.

## 9. Agentless Lite — a minimal direct benchmark baseline

[Author repository](https://github.com/sorendunn/Agentless-Lite) (2025).
Read: README method, retrieval, artifacts and Multimodal announcement.
**Repository documentation only; code and results not re-executed.**

- [SRC] Reports SWE-bench Multimodal experiments and released retrieval/run
  artifacts. Its workflow retrieves relevant repository files with embeddings
  and prompts for a repair, retrying for a valid patch without requiring a
  runtime environment.
- [INF] A useful low-complexity repair baseline. “A valid patch was emitted”
  is not self-verification. Match its information access and count retries in
  our budget comparisons; do not inherit prepared retrieval contexts without
  checking what they contain and how they were produced.

## 10. CodeV / Visual SWE-bench — inexpensive modality-to-text baseline

[Author repository](https://github.com/luolin101/CodeV).
Read: README workflow. The prior local dataset audit inspected its video-only
JSON at commit `46a6b65bf57f24cd33eddbc2445583939207df37`:
[audit](../notes/2026-10-20-public-dataset-audit.md).

- [SRC] Converts image/video material into textual issue context, then feeds
  existing text-based repair approaches. Supplies a SWE-bench-style harness
  and a gold-patch evaluation option. README warns that visual-model JSON may
  need manual correction.
- [RUN] The prior audit found one task in that revision's video-only subset;
  it did not establish a runnable oracle for it.
- [INF] Use caption/transcript-to-existing-harness as a cheap ablation, while
  preserving source frames and timestamps for inspection. Do not silently hand
  repair malformed model outputs when measuring autonomous success. Visual
  SWE-bench is a separate source; do not assume it is the official Multimodal
  release or evidence of broad video coverage.

## 11. SWT-Bench and ReProAgent — evaluating the generated test itself

Mündler et al., [SWT-Bench paper](https://arxiv.org/abs/2406.12952),
[harness](https://github.com/logic-star-ai/swt-bench);
Zhang et al., [ReProAgent v1](https://arxiv.org/html/2607.09123v1) (2026).
Read: SWT formulation/metrics/method (early v1 HTML has a different title);
current harness README; ReProAgent task formulation and stage/tool design.

- [SRC] SWT transforms repair instances into **test-generation** tasks:
  generated tests run against buggy and gold-fixed code, with change coverage
  as an additional measure. This is based on Python SWE-bench, not its
  Multimodal variant.
- [SRC] ReProAgent stages localization, root-cause analysis, test planning
  and generation, using repository/runtime tools and semantic review of
  failures. Its evaluated test-generation datasets are SWT subsets.
- [INF] Measure applicability, reason-for-failure, valid reproduction and
  independent fix correctness separately. A malformed import or unrelated
  crash is not useful claim evidence merely because a command exits nonzero.
  Reuse an existing agent with a test-writing instruction before adding a
  multi-role controller. Change coverage is informative but not an oracle.

## 12. ReBug — browser prerequisites and the meaning of reproduction

*From Bug Reports to Browser-Executable Procedures* (August 2026 preprint).
[Paper v1](https://arxiv.org/html/2608.03598v1).
Read: preparation/execution/evaluation §III and dataset/protocol §IV.

- [SRC] Reconstructs missing prerequisites and input artifacts, plans browser
  interactions, and uses live screenshots/DOM plus typed actions and execution
  traces. An LLM judge compares the final browser state to annotated outcomes.
- [SRC] Most evaluation uses controlled current deployments rather than
  restoring every historical buggy snapshot. A smaller historical replay
  study complements the main procedure-execution evaluation.
- [INF] Useful for logins, uploads, seed data and navigation that clips omit.
  Its main success measure must not be substituted for our historical
  fail-before/pass-after requirement: completing a report-derived procedure on
  a current deployment and reproducing the original defect are distinct.
  Preserve the distinction between prerequisites prepared successfully and an
  assertion that actually exposed the intended bug.

## 13. SWEeper-Bench — browser discovery and independent preservation checks

[Author project](https://sweeperbench.com/) (accessed 2026-10-20).
Read: task protocol, verifier validation and worked example on the project page.
**Project documentation; paper/code audit not performed.**

- [SRC] Starts with an area-level request to discover and fix an interactive
  bug. Each task has a target behavior procedure and a preservation procedure,
  evaluated by a browser verifier. The authors describe calibrating verifiers
  on buggy versions and reference fixes with repeated configurations.
- [INF] Directly relevant to “use the app to check your work,” although its
  input is not a meeting recording. Borrow target/preservation separation and
  verifier calibration. Model-driven browser verdicts introduce their own
  variance and false-acceptance risk; executable assertions remain preferable
  where the claim permits them. Do not infer that benchmark task/procedure
  availability includes redistribution rights to associated recordings.

## 14. Replay Web Debug Bench — rich recordings for diagnosis, not repair proof

[Author announcement](https://www.replay.io/blog/web-debug-bench)
(2026-04-07). Read: benchmark definition, generation/cleaning, scoring and example.

- [SRC] Synthetic agent-built web-app failures carry repository state,
  a Playwright error and optional Replay recording. MCP debugging evidence
  supports root-cause explanation and source-location identification; scoring
  uses location comparison and model judges. The pipeline reproduces failures
  and refines diagnostic answer keys.
- [INF] Instrumented browser recordings can be much richer than pixels:
  network, state and execution traces may explain hidden causes. Keep them as
  an optional evidence channel with provenance. This benchmark's explanation
  success does not establish a correct source patch, an executable
  recording-derived assertion, or suitability as an off-the-shelf repair oracle.

## 15. Earlier video-to-replay and video-to-text work

These are precedents, not direct SWE-bench Multimodal extensions.

| Work and inspection | Method / useful lesson | Boundary for this project |
|---|---|---|
| [V2S+](https://arxiv.org/html/2301.01191v1), Bernal-Cárdenas et al. (2023); introduction, detection/classification and replay design | [SRC] Detects recorded touch indicators and classifies gestures to synthesize Android replay. [INF] Explicit interaction markers reduce ambiguity. | [INF] Touch/gesture replay does not specify the correct outcome or repair the code; arbitrary meeting clips may lack the markers. |
| [GIFdroid](https://arxiv.org/html/2112.04128v1), Feng & Chen (2021/2022); introduction and approach | [SRC] Extracts video keyframes, matches them to an app UI transition graph and derives a replay route. [INF] Recover the path to a recording that starts mid-flow. | [INF] Prebuilt graph coverage and dynamic UI mismatch are dependencies to measure, not free context. No verified source fix follows from replay alone. |
| [CAPdroid](https://arxiv.org/html/2302.00886v1), Feng et al. (2023); introduction, approach overview | [SRC] Segments recordings and captions inferred actions to assist human replay. [INF] A useful action-text baseline distinct from speech transcription. | [INF] Describing actions, recognizing the bug and deriving its expected behavior are separate tasks. Captions do not provide executable assertions. |
| [JANUS](https://arxiv.org/abs/2407.08610), Yan et al. (ICSE 2024); abstract and author-hosted introduction/method overview | [SRC] Combines visual scene representations, OCR text and temporal alignment for duplicate-video retrieval. [INF] Preserve ordering and the bug-revealing endpoint in retrieval experiments. | [INF] Duplicate detection is not repair or verification; its retrieval results cannot establish our moment retrieval or reproduction rate. |

## What this means for our MVP

The current design already plans a frozen reproduction, held-out native
regressions and Harbor oracle/nop checks. Those are complementary controls:
they establish a changed executable outcome and resistance to some regressions.
They do **not** prove that the extracted claim captured the recording's intent,
that the reproduction exercises the visible failure, or that a passing fix
preserves every relevant behavior. These remaining gaps follow from the
different verification targets above. [INF]

Practical implications, without changing milestone gates in this document:

1. **Bind claims to evidence before writing a fix.** Save the exact clip span,
   observed symptom, expected behavior and any uncertainty separately. If the
   expected behavior is not stated or visibly established, ask or abstain;
   do not let the fix manufacture the requirement. [INF]
2. **Freeze evidence as well as tests.** Keep the pre-fix failure log, assertion,
   source/media hashes and browser state. If a reproduction changes, treat it
   as a new candidate that must pass the original admission process. [INF]
3. **Challenge weak assertions.** On selected cases, try a feature deletion,
   error swallowing and an example-specific shortcut. Record each as an
   explicitly authored negative control; do not describe a small challenge
   set as a comprehensive mutation score. Add independent expected-output or
   neighboring-behavior assertions when those controls reveal a hole. [INF]
4. **Keep gold-derived knowledge out of generation.** Separate evaluator
   process/storage from the agent-visible repository/context and retrieval.
   Track any development-case memory and deduplicate related issues before
   splitting. Frozen tests alone do not remove contamination. [INF]
5. **Calibrate any visual judge.** A supplemental browser/VLM verdict needs
   known-buggy and known-fixed controls, including harmful-but-visually-changed
   patches. Save disagreement and inconclusive states; a timeout or inaccessible
   page is not a semantic failure/pass. [INF]
6. **Measure the modality's contribution.** Compare issue text only,
   captions/transcript, unordered sampled frames, and ordered frames/clip under
   the same model and spend bounds. Report claim grounding, reproduction and
   held-out repair success separately, with sample sizes and intervals.
   Silent GIF success establishes neither narration nor meeting coverage. [INF]

Our strongest defensible contribution would be measured reliability of that
whole chain and portable evidence-bearing tasks. “An agent looked at a screen
and liked its fix” is already a studied workflow and is a weaker assurance
than the one this project is trying to build. [INF]
