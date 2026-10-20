# M1 ingestion and retrieval implementation

[CODE] Every visual recording is sampled on the same 45-bin midpoint grid.
Source frame timestamps are decoded with ffprobe, then the latest frame at or
before each sample is selected by frame index. This handles GIF final-frame
holds and avoids silently taking a later packet. A controlled two-frame GIF
test covers both temporal ordering and the final hold. The full suite passes
72 tests, including actual HTTP calls to find_moment/get_screen_text.

[RUN] An initial seek-based pilot and one additional caption response were
archived under ignored `data/runtime/visual-index-seek-baseline-abandoned/`.
Another input failed in local decoding before a generation request. These costs
remain in the shared ledger. The first exact-timestamp batch (exec 34917, now terminal) then
hit MAX_TOKENS on repeated console OCR in 1638. Four completed indexes plus
the incomplete metered response are archived under ignored
`data/runtime/visual-index-unbounded-captions-abandoned/`; summary in
`notes/runs/m1-ingestion-aborted.json`. The bounded-caption baseline reruns all
eleven cases under one consistent prompt, before any retrieval measurements.
The bounded sequential batch (exec 6879) is terminal: all eleven indexes
were produced. No visual ingestion batch should be restarted.
Outputs bind media/corpus/prompt/model/sampler identities.

[CODE/INF] The prospective comparison uses the same 45 captions, query and
caption budget for both methods: fixed45 searches individual caption/screen-text
documents with SQLite FTS5 BM25; temporal3 searches each frame with its immediate
neighbors concatenated. Query tokens are quoted and stopwords removed. No source
patch, supplied test, test name, gold annotation or issue text enters captioning.
Human claim text is an evaluation-only retrieval query, equally available to
both methods. This is a deliberately small temporal-window comparison, not an
embedding or scene-selection quality claim. `scripts/evaluate_m1.py` preserves
all eleven cases, including missing outputs, and computes the frozen Wilson
gates, strict overlap, distances and midpoint control. Prefer fixed45 unless
windows improve strict hit@1 without losing either permissive hit metric.

[CODE] The server owns registered media and index paths. MCP clients supply
identifiers, bounded intervals/questions and result counts. Retrieval results
are explicitly model captions requiring frame confirmation; recognized screen
text is labeled fallible. Index loading checks media/corpus identity. No paid
model request occurs inside a read-only MCP tool.

[CODE] Audio ingestion decodes mono 16kHz WAV in at most 20-second chunks,
transcribes through the same guarded model and validates timestamp bounds,
speaker-label format and text. Speaker labels are uncertain and chunk-local;
there is no cross-chunk identity matching. Raw metered responses are persisted
before parsing and reused on resume. Silent inputs explicitly return no_audio.
The audio functional smoke uses synthetic espeak-ng speech and will be run after
the visual batch, keeping paid requests sequential. It cannot establish human
meeting transcription or diarization quality.

[CODE] Commands (from the repository after installing all extras):

```sh
uv run --all-extras svh ingest --recording swebench-bpmn-1655
uv run --all-extras svh ingest
uv run --all-extras svh budget
uv run --all-extras svh mcp
.venv/bin/python -I scripts/evaluate_m1.py
.venv/bin/python -I scripts/smoke_audio_ingest.py
```

[RUN] The eleven-case lexical comparison failed the fixed M1 gate. Fixed45:
hit@1 8/11, Wilson 95% [43.44%,90.25%]; hit@5 9/11 [52.30%,94.86%].
Temporal3: hit@1 and hit@5 9/11 [52.30%,94.86%]. Strict hit@1 is 3/11
[9.75%,56.56%] for both, equal to midpoint. Strict hit@5 is 7/11
[35.38%,84.83%] for fixed45, 5/11 [21.27%,71.99%] for temporal3 and 3/11
[9.75%,56.56%] for midpoint. The prospective simplicity rule retains fixed45;
neither method passes. Complete results: `notes/runs/m1-lexical-baseline.json`.
No gold corpus, threshold, caption prompt or frame sample is changed in response
to these retrieval measurements. A local semantic candidate will use the same
frozen caption evidence and be measured separately; no improvement is claimed.

[RUN] Audio smoke passed: one synthetic sentence transcribed exactly with one
bounded segment, no speaker identity claim. `notes/runs/audio-ingest-smoke.json`.
Updated actual CLI/HTTP smoke also passed find_moment and get_screen_text:
`notes/runs/mcp-http-smoke.json`. Total settled API cost, including every
abandoned attempt and audio smoke: $0.464144; no unsettled requests at that
checkpoint. Model outputs/raw captions remain ignored, with hashes and usage
recorded in reports. M1 remains incomplete because its retrieval gate failed.
