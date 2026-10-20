# SWE-bench Multimodal: primary-source audit and first native pilot

## Selection and maintenance

- [SRC] The [official page](https://www.swebench.com/multimodal.html) announces
  Multimodal v2 on 2026-09-01: 480 reproducible test tasks, rebuilt Docker
  environments, grading/asset fixes and removal of flaky/ungradeable cases.
- [RUN] GitHub API inspection found main HEAD
  `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e` dated 2026-09-02; repository metadata
  reports not archived, with `pushed_at` 2026-09-18. These timestamps show recent
  activity, not a guarantee that every task works. The local reference clone
  `/home/d3rrick/swe/llms/SWE-bench` is at that same HEAD.
- [INF] Use this as the primary visual-task source. Keep a single implementation
  branch; separate source adapters and evidence records suffice for these
  experiments. CodeV and the E2E dataset remain alternatives.
- [INF] An executable benchmark can evaluate newer multimodal models without
  changing its tasks. Its age/maintenance does not establish difficulty for
  current models, lack of contamination, or the benefit of its media. Measure
  those separately with held-out cases and a video-versus-text-only comparison.
  No current-model scores or comparative capabilities were measured here.

## Actual released data

- [RUN] Downloaded both Parquet files at dataset revision
  `4e6662d51c48e475f7f346e4fa09a6f8b31fcaa5`; checked their SHA-256 values against
  the Hub's file metadata. The isolated optional PyArrow reader audited
  **100 dev + 480 test rows**. It found **2 tasks with explicit video URL
  extensions, 67 with GIF URLs, and 8 with unresolved extensionless asset links**.
  Categories may overlap and untyped media may add videos. This is a URL
  inventory, not a decoded-media census or a pass-rate estimate.
  Exact candidates, revision and hashes: `notes/runs/swebench-multimodal-audit.json`.
- [RUN] The video tasks are `processing__p5.js-6111` and
  `bpmn-io__bpmn-js-1655`. The selected BPMN row was also compared structurally
  against the pinned Parquet source, not just trusted from the dataset viewer.
- [CODE/INF] Selected BPMN first because its external-label color claim maps
  directly to its single FAIL_TO_PASS test. The p5.js row includes many unrelated
  file/download test failures and needs additional triage. Its initial image
  download was stopped; no p5.js task was run.

## First task and execution boundary

- [RUN] The BPMN issue's MOV downloaded successfully: 388344 bytes. `ffprobe`
  reports 6.816667 seconds, 532×494 H.264 video, with no audio stream. Inspected
  frames at 2 and 6 seconds show the diagram selection and resulting pale label.
  Only sampled frames were reviewed; full-frame privacy review and timestamp
  annotation remain necessary before admitting or redistributing a task.
  Source: `https://user-images.githubusercontent.com/25825387/169325524-f91870f7-c0e5-4b43-999f-4045eeeb2697.mov`;
  SHA-256: `91ba9104f87ed026fc743653f6fcfd692773eb5b93599d702e8423b9e1b38aed`.
- [SRC] Read the source repository's license at the supplied base revision:
  it permits software use/modification with attribution and preservation of the
  bpmn.io watermark. That is separate from media/dataset redistribution rights;
  no source media, patches or underlying application code is committed here.
- [CODE] `scripts/pilot_swebench_task.py` runs the row's supplied evaluation script
  and gold fix in fresh containers from an immutable image digest. It mounts only
  an input bundle read-only, blocks networking, limits resources, and grants
  SETUID/SETGID because the native script changes to its browser user. No owner
  environment or Docker socket is exposed inside the container.
- [CODE] The pilot guards test-patch application, captures the test command's own
  exit code, and checks the expected assertion and positive suite completion.
  The upstream script's final checkout otherwise masks the test command's exit
  status. Existing unrelated skips are recorded and must remain unchanged;
  they do not count as successful reproduction evidence.
- [CODE] Fix and test patches stay in the ignored source directory. Their hashes
  and the identical executed evaluation-script hash belong in the proof report.
  This tests a supplied oracle; it does not measure agent-generated tests/fixes.

## Reproduction commands

From the repository root, with Docker available:

```sh
hf download SWE-bench/SWE-bench_Multimodal --type dataset \
  --revision 4e6662d51c48e475f7f346e4fa09a6f8b31fcaa5 \
  --include 'data/*.parquet' --include README.md \
  --local-dir data/external/swebench-multimodal
uv sync --extra datasets --locked
uv run --extra datasets python -I scripts/audit_swebench_multimodal.py --export-pilot
docker pull swebench/sweb.eval.x86_64.bpmn-io_1776_bpmn-js-1655@sha256:84f2d5f6c527bff4e80d433dfb46a48abee3d7bcddffe5f1149230d9528c05df
python -I scripts/pilot_swebench_task.py
```

For grading-code changes, `python -I scripts/pilot_swebench_task.py --regrade`
checks saved input/log hashes and regrades without rerunning the containers.

## Observed result

- [RUN] The supplied oracle/gold-fix pilot succeeded: **1/1 case**, Wilson 95%
  interval **[20.65%, 100%]**, computed with `svh.oracle.wilson(1, 1)`.
  This is a single selected case, not a benchmark-wide performance estimate.
  Evidence: `notes/runs/swebench-bpmn-pilot.json`.
- [RUN] Pre-fix: 1777 executed, 1784 discovered, 7 skipped; **1 failure and
  1776 passes**. The expected external-label color assertion failed, comparing
  `#ff00ff` with `#ffff00`. Post-fix: the same 1777 executed and 7 skipped,
  **1777 passes**. Test-command exit codes changed from 1 to 0.
- [RUN] Initial grading conservatively rejected suite completion because of the
  existing skipped tests. Updated the accounting to require executed + skipped
  = discovered, positive completed execution, the expected pre-fix assertion,
  a successful post-fix suite, and unchanged skip/discovery counts. Regraded the
  same hash-checked logs; did not change or rerun the source, fix, or tests.
- [RUN] Final repository checks: 27 tests passed; `git diff --check` clean.
  Both execution containers were removed by the runner.
- [CODE] External raw logs remain in the ignored source directory. The committed
  proof records raw-byte and decoded-text hashes separately (terminal progress
  output contains carriage returns), plus a short assertion excerpt.
- [INF] Next unit: add an external-source annotation/provenance adapter, including
  native runner support and immutable base+patch source states, screen the whole
  clip, then expand the M0 sample with reviewed temporal media. Do not count this
  supplied-oracle pilot as an agent-generated reproduction or a completed M0 item.
