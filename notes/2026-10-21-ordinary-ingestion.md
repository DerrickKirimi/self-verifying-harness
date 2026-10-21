# Ordinary recording ingestion and retrieval

[CODE] `svh ingest --task-manifest ...` now creates the same bounded caption and
screen-text representation used by corpus ingestion, without benchmark rows,
gold source/test patches or admission. Cache paths are owner-only and bound to
the manifest SHA256. Audio uses the existing transcript route. Model responses
are retained before parsing, so resuming does not silently regenerate them.

[CODE] The default search is the lexical baseline. Explicit `--semantic` uses
the reviewed local text-only embedder and observation query, with caption/vector
hash integrity. The MCP process loads the selected policy and private index from
the server-owned task cache; model tools cannot select arbitrary index paths.
Corpus paths and selected corpus policy are unchanged.

[RUN] Executed `.venv/bin/svh ingest --task-manifest
data/runtime/demos/readme-e2e-20261021/task.json --semantic`: 45 captions, no audio,
selected local embedding retrieval. The cumulative ledger changed from $3.227571
to $3.251483 ($0.023912 estimated additional charge), leaving $0.748517 under the
unchanged $4 cap, zero pending at that read. It is not a provider receipt.

[RUN] Executed `scripts/smoke_task_evidence.py` against that manifest. Actual MCP
metadata, a decoded PNG, two locally embedded search matches and indexed screen
text all returned successfully. Public summary:
`notes/runs/ordinary-indexed-mcp-smoke.json`. The smoke made zero model calls;
raw MCP logging remains ignored under the task cache. The usage guide contains
the repeatable commands.

[RUN] Full regression suite: **104 passed**, `.venv/bin/python -I -m pytest -q`.
Added tests cover ordinary ingestion/resume without dataset dependencies, cache
isolation when the manifest changes, and semantic vector integrity in both corpus
and ordinary-task paths.

[INF] This validates normal-input plumbing, not new-recording search quality.
Captions/OCR/transcripts remain fallible. The full M3 acceptance gate and human
semantic adjudication remain incomplete; a working demo alone does not close them.
