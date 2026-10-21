# First generated recording-to-repair demonstration

[RUN] SWE-bench Multimodal case1679, candidate2, completes the actual path:
registered recording -> extracted/refined claim -> existing deepagents SDK ->
model-generated Chrome check -> observed target assertion failures -> frozen
check -> model-generated source-only fix -> unchanged check passes -> independent
native regressions pass. No benchmark gold source patch or supplied test patch
was sent to the generation model.

[RUN] Both primary tests operate the replace popup, establish standard-loop state,
observe the parallel/sequential SVG markers, then fail specifically because the
exported XML retains `standardLoopCharacteristics`. They both pass after the
model-generated type-check correction in `lib/features/popup-menu/ReplaceMenuProvider.js`.
The independent native suite executes **1792 tests**, all passing, with **7
unchanged skips**, **1799 discovered**. Proof and exact model-output hashes are
in `tasks/generated-v1/swebench-bpmn-1679/tests/proof.json`.

[RUN] A finite authored challenge set rejects feature deletion and a try/catch
error-suppression non-fix by assertions. A fixture-identifier shortcut passes the
original primary check; this exposes a real weakness. An independent Task ID
variation rejects it. That independent check was itself observed failing by
assertion on buggy source and passing with the generated source fix before being
added to the Harbor verifier. These six challenge observations are retained in
`data/runtime/m3/generated-v1/swebench-bpmn-1679/2/challenges/`; this is not a
comprehensive mutation score. The primary generated check is unchanged.

[CODE/RUN] The Harbor package uses schema1.4, a fresh separate verifier and only
collected source artifacts. Harbor restores artifacts to their original source
paths, not host collection destinations; a pristine library copy in the verifier
image validates source-only transfer. Raw media stays reference-only. Upstream
source license is retained. The package's own hashes must pass before trials.

[RUN] The first real nop trial fails in infrastructure because Buildx is absent;
it produces no reward and is explicitly not a nop pass:
`notes/runs/harbor-generated-v1-1679.json`. Official Buildx0.38.1 is now installed
only under ignored project directories, with both release-asset and published
checksum verification. The new actual nop/oracle pair (exec82768) is terminal and passes: **nop reward0**,
**oracle reward1**, with actual primary/independent browser and native-suite
observations checked alongside rewards. Exact task bundle hash and trial result
hashes: `notes/runs/harbor-generated-v1-1679-buildx.json`. No model requests were
used for these trials.

[RUN/INF] This is one development demonstration. The all-eleven M3 checkpoint is
**1/11**, Wilson95% **[1.62%,37.74%]**, with only five artifacts considered so far.
The gate remains **failed/incomplete**, not a shipped MVP or a generalization
claim. Earlier setup/alignment failures, pre-existing passes and empty outputs
remain retained; the method evolved during development. See
`notes/runs/m3-generated-v1-checkpoint.json`.

[RUN] Guard ledger after source repair: **$3.113287 settled**, **$0.886713
available**, no unsettled requests; cap remains **$4.00**. These are local guarded
cost estimates from metered token usage, not a provider billing receipt. Model:
Gemini3.8Flash, medium thinking; source-only repair inspection capped at three
read calls after the complete frozen check/observed failures were supplied.
Independent human adjudication is still outstanding; alignment review is
explicitly Codex AI-assisted.
