# Release audit: source edit path format

[RUN] V5 case1638 candidate1 generated an actual two-path target assertion, then
returned a source repair with absolute path
`/workspace/lib/features/label-editing/cmd/UpdateLabelHandler.js`. Its old/new
replacement proposes deleting the retained DI label. The controller rejects
that path before applying any patch, because `apply_edits` and `allowed_source`
require a relative `lib/...js` path. No post-fix success is inferred from intent.
Raw output/error remain in the ignored candidate directory. This is retained as
a failed repair under the unchanged v5 method; candidate2 is separately allowed.

[RUN] Candidate2 subsequently returns its own relative-path source edit, without
manual correction, and completes actual frozen fail/pass plus1772 native passes,
seven unchanged skips. Its source file is byte-identical to the existing
canonical1638 task. The original rejected output stays rejected; this later
success does not erase the interface ambiguity. Evidence:
`notes/runs/m3-standard-submission-v5-1638-repair.json`.

[CODE/INF] The common prompt requires absolute paths for file tools while the
repair prompt requires relative paths for edit output. `SourceEdit.path` is a
plain string without a schema description/pattern. This is avoidable interface
ambiguity. After the current pinned run, provide a clear typed output contract,
or strictly normalize only the canonical `/workspace/lib/...` prefix before the
same traversal/extension/allowlist checks. Never accept arbitrary absolute paths,
`..`, alternate roots or silently changed source replacement strings. Exercise
the actual captured output in an isolated replay and preserve the original
failure rather than rewriting the model trace or retrospectively changing its
benchmark outcome. Do not edit pinned generation code during v5.

## Resolution

[RUN] Resolved after the frozen evaluation. `notes/runs/source-path-alias-replay.json` records actual captured-output pre-fail/post-pass and1772 native passes with seven skips, without generation or retroactive benchmark changes. Only the exact workspace alias is normalized; invalid/traversing paths are rejected before backend access. All148 harness tests pass.
