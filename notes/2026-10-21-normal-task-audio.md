# Narrated ordinary recordings reach claim extraction

[CODE] The ordinary runner previously ignored its recording's audio during claim
extraction, and its MCP child had no transcript cache to load. It now transcribes
bounded chunks before extraction under the existing budget guard, stores results
in a manifest-bound owner-only directory, and reloads those bytes for the separate
MCP evidence process. Ordinary run directories are owner-only too.

[CODE] Audio input appends a dedicated prompt and a timestamped transcript to
extraction, binds a transcript SHA256 into response identity, and permits
`expected_source=spoken`. Silent extraction prompt/identity bytes are unchanged.
The read-only code checkpoint must independently call `get_transcript` for audio
input. Issue-only output cannot claim spoken grounding. No speaker label grants
identity or authorization.

[RUN] Full suite: **102 passed**, `.venv/bin/python -I -m pytest -q`.
The added integration test creates an actual two-second synthetic video/audio
file, decodes its WAV through ffmpeg, uses a deterministic transcription response,
reloads it through the exact normal-task loader used by the MCP child, verifies
private cache permissions and resumes with no second model invocation. Another
test verifies transcript delivery to extraction, spoken-source handling and
rejection of a cached response after transcript changes.

[INF] This is data-flow evidence, not human narration accuracy or live speech
evaluation. The earlier synthetic Gemini transcription measurement remains the
only actual provider audio smoke. Ordinary visual indexing/retrieval still needs
its own product entry point; this change does not claim full MVP completion.
