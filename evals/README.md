# Evals

M0 evaluation set: annotated bug walkthroughs (`docs/roadmap.md`).

- `schema/walkthrough.schema.json`: one JSON file per walkthrough, in `annotations/<id>.json`.
- `recordings/`: the video files. Gitignored; keep them local or use Git LFS. The owner's voice and apps only.
- `reproductions/`: one Playwright or pytest file per claim.
- The `observed` fields are written by the oracle/nop runner, never by hand. A claim counts only when `fails_on_pre_fix` and `passes_on_post_fix` are both true.
