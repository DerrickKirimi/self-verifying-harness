# Avoid repeated matching over accumulated browser progress

[RUN/CODE] An interrupted duplicate scorer showed it spending time in
`svh.native.evidence`'s repeated failure-header regex search. Karma accumulates
progress with carriage returns; searching the whole log and then every line for
every expected failure repeats work across progress messages.

[CODE] The parser now splits progress into lines and collects complete failure
headers once, before attaching assertion excerpts to expected tests. Suite
completion, exit code, test coverage and assertion requirements remain required.
The scorer also binds the exact report bytes read and rejects a report that
changes during scoring, avoiding mixed concurrent snapshots.

[RUN] Full suite: **105 passed**. A new regression input includes two thousand
carriage-return progress updates, an actual assertion failure and a complete
suite; progress alone cannot manufacture a failure. Actual frozen-corpus
revalidation and M3 rescoring completed, producing a byte-identical score to the
pre-change checkpoint: `notes/runs/native-parser-score-comparison.json`. All
eleven source/admission proofs therefore still satisfy their original gate.
No speedup ratio or timing benchmark is claimed.
