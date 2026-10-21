# Audio-only input closes an original MVP gap

[SRC/CODE] The original idea's MVP input explicitly includes a `.wav` audio file
(`docs/idea/self-verifyingmultimodal-harness.md:544`). Normal registration still
required a video stream and extraction/generation always demanded frames. That
excluded audio-only input despite a working lower-level transcription function.

[CODE] Registration now accepts finite audio-only media under the existing
size/duration limits. It transcribes bounded chunks into the manifest-bound
private cache; ingestion omits visual captioning. Moment retrieval uses explicit
lexical transcript search. Frame and screen-text tools return `no_video`.
Extraction and the existing deepagents code checkpoint use reported spoken
observations, require actual transcript reinspection, and reject `shown` source
claims for audio-only input. Generation receives the actual MCP transcript and
no images. Executable browser verification remains mandatory for software claims.
Silent public-corpus prompt paths and its acceptance rubric remain unchanged.

[RUN] Full suite: **111 passed**, `.venv/bin/python -I -m pytest -q`. Added tests
cover actual WAV registration/decoding, cache/search resume, source-byte mutation
rejection, transcript-only extraction/controller context, and accepting a code
checkpoint only after transcript reinspection. No paid model is used in tests.

[RUN] `scripts/smoke_audio_only.py` then generated synthetic eSpeak narration,
used the budgeted actual Gemini transcription path and exercised all five tools
through authenticated MCP. It also invoked the actual generation-context helper:
transcript received, no images. Report:
`notes/runs/audio-only-provider-mcp-smoke.json`,9.363719s input,two transcript
segments. Ledger at completion: $3.324319 estimated charged/reserved,$0.675681
available,zero unsettled,unchanged $4 cap. Script and running instructions persist.

[INF] This proves functional audio-only routing with synthetic speech, not human
narration/diarization accuracy. It does not establish a fresh generated fix or
close the eleven-case M3 gate. A subsequent ordinary audio run is measured
separately rather than being added to the frozen public denominator.

[RUN/INF] Public1610 used both allowed check versions and reached an assertion
only by setting the canvas root to its current value. It never navigated away;
its alignment review rejects that no-op as evidence of the recorded plane-switch
bug. No source repair was attempted for that invalid reproduction.
