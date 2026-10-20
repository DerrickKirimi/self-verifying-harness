# Public video + software-task dataset audit

Research checkpoint, 2026-10-20. No external task was executed or admitted to
the eval set. Downloaded data remains isolated under `/tmp/svh-datasets/`;
no external scripts were installed or run. Python inspection used `python -I`.

## E2E Tests Dataset: closest browser-recording match

- [SRC] [Repository](https://github.com/e2e-tests-dataset/e2e-tests-dataset)
  documents six injected regressions across three Spring web apps, failing and
  fixed tags, tests and Docker instructions. The
  [paper](https://doi.org/10.1007/s11219-021-09566-x) describes videos of test runs.
- [RUN] GitHub recursive tree at `cfc3aa4641ee2083a5bd9309e7ba860966e9771b`
  contains **10 MP4 files in five regression directories**, each with a buggy
  and fixed video. No MP4 is listed for Application-1/regression-2.
  Source: `https://api.github.com/repos/e2e-tests-dataset/e2e-tests-dataset/git/trees/cfc3aa4641ee2083a5bd9309e7ba860966e9771b?recursive=1`.
- [CODE] Read Application-1/regressions/regression-1/README.md: an Add List
  control updates the wrong collapse variable; tags are `regression-1` and
  `regression-fixed-1`; the documented runner is Maven TestE2EFront.
  `.gitmodules` links the three application repositories.
- [RUN] Downloaded that case's buggy video (790808 bytes). `ffprobe` reports
  5.360000 seconds, H.264 video **and an AAC audio stream**. We have not listened
  to it or established narration/privacy suitability. Do not label it silent.
- [SRC] Root README calls for Java 1.8 and Node 8.x. [INF] Rebuilding this legacy
  stack may need environment repair; Docker instructions do not prove it runs now.

## CodeV / Visual SWE-bench: smallest Python video-task candidate

- [SRC] [Repository](https://github.com/luolin101/CodeV) documents its visual
  dataset and Docker evaluation harness, including gold-patch evaluation.
- [RUN] Inspected `Visual SWE-bench/list_data_onlyvideo.json` at
  `46a6b65bf57f24cd33eddbc2445583939207df37`: **one task**,
  `matplotlib__matplotlib-25631`. Both `patch` and `test_patch` are nonempty;
  it provides `base_commit`, `FAIL_TO_PASS` and `PASS_TO_PASS`.
- [CODE] The issue concerns `bbox_inches="tight"` during animation frame
  capture; its problem statement links actual and expected output videos.
  These are animation outputs, not narrated browser walkthroughs. The repository
  tree also lists two MP4s under that task's Videos directory.
- [INF] This is a useful first Python/pytest external oracle pilot, but one task
  cannot fill M0, and output-video interpretation differs from listening to a
  bug walkthrough. No claim is made that its tests still execute or fail/pass here.

## SWE-bench Multimodal: broader source to filter

- [SRC] [Current dataset card](https://huggingface.co/datasets/SWE-bench/SWE-bench_Multimodal/blob/main/README.md)
  describes mixed visual assets including screen recordings, base revisions,
  patches, tests, fail-to-pass fields and Docker evaluation.
- [RUN] Used `hf datasets card ... --text` and `hf datasets list ... --recursive
  --format json`. The README's last listed revision is
  `4e6662d51c48e475f7f346e4fa09a6f8b31fcaa5`. No Parquet rows were inspected.
- [SRC] Card prose and embedded split metadata disagree about dataset counts;
  do not copy its headline totals into our eval statistics. [INF] Filter actual
  released rows for video availability and executable tests before selecting cases.

## Other candidate and remaining checks

- [SRC] [TANGO](https://two-to-tango.github.io/tango/) publishes user-study bug
  videos and duplicate-detection artifacts. The overview read does not establish
  a ready-made failing/passing code-repair oracle. [INF] Lower priority for M0.
- [RUN] GitHub API returned `license: null` for the E2E and CodeV repositories;
  their inspected trees did not list a license file. This does not establish
  redistribution permission. Check dataset, media and underlying code permissions
  separately before importing/publishing artifacts. No third-party media is committed.
- [INF] Next single implementation unit: inspect reuse permission and pilot
  CodeV's video task in Docker with the original tests and gold patch; record an
  actual pre-fix assertion failure and post-fix pass. If unsuitable, try an E2E
  browser case. Keep fix/test patches out of the solver's inputs.
- [INF] Separate visual verification from speech evaluation. Public visual cases
  can exercise the former; owner narration or suitably licensed narrated cases
  can later exercise STT/claim extraction. Synthesized narration, if added,
  must be explicitly labeled and cannot measure natural spoken-claim performance.
