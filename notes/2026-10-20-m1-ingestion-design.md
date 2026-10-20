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
remain in the shared ledger. The corrected batch is running sequentially in
exec session 34917; do not restart it while active. Its script was loaded before
the later process-lock addition. No other ingestion process should run until
it terminates. Outputs bind media/corpus/prompt/model/sampler identities.

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

[INF] M1 is not yet passed. Retrieval measurements and the actual audio
functional path are still pending; do not infer their outcome from unit tests.
