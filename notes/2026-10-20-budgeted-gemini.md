# Budget-covered Gemini transport

[CODE/RUN] `svh.gemini.BudgetedGemini` wraps the provider generation methods,
so ordinary calls, tool-bound calls and direct summarization calls share the
persistent ledger. Public stream/astream use nonstreaming generation. Private
provider streaming is disabled. Each request reserves the authenticated maximum
input context plus the configured output cap, at reviewed standard rates.
Only a single metered result settles it; timeouts/missing usage retain the full
reservation. This intentionally sacrifices available capacity near the cap.

[SRC/CODE] Installed google-genai 2.31.0 normalizes retry attempts=0 to one
attempt (`_api_client.py`). We force one attempt on the final request. Installed
LangChain summarization independently wraps its model with `with_retry`; the
budgeted model also constrains that wrapper to one attempt. Context-overflow
reformulations, if performed upstream, still pass through a fresh reservation.
Output usage already includes thinking tokens in langchain-google-genai 4.4.2;
reasoning detail is not added again.

[RUN] Authenticated metadata-only requests confirmed access to
`gemini-3.5-flash-lite` and `gemini-3.8-flash`, each with input limit 1,048,576
and output limit 65,536. No content was generated in this probe. Sanitized
metadata: `notes/runs/gemini-model-metadata.json`.

[SRC] Prices rechecked 2026-10-20 against
https://ai.google.dev/gemini-api/docs/pricing : standard input/output including
thinking, USD per million: Flash-Lite 0.30/2.50; Flash 0.75/3.75 through
2026-12-31. Policy requires metadata and price review within 24 hours, rejects
unreviewed model/date combinations and never automatically refreshes prices.

[CODE] Factory explicitly selects Developer API and the official endpoint;
ambient Vertex routing is rejected. Only reviewed configuration fields, inline
PNG/JPEG/WAV and local function declarations are allowed. Provider-hosted tools,
caching, image generation, candidate multiplication, output-cap overrides,
remote files/video and unreviewed options cannot reach transport. Secret files
must be owner-only regular files without symlinks; values are never shell-evaluated.
The local $4 cap can be lowered but cannot increase on restart. Model responses
and source artifacts cannot choose credentials or prices.

[RUN] Eleven transport tests pass, including sync/async, stream/astream,
bind_tools, actual sync/async summarization middleware, ambiguity, exhaustion,
expiry, disallowed options and private configuration. The full suite passed
68 tests before the final additional request whitelist and async summary check;
the affected eleven tests passed again afterward. No paid generation yet.

[INF] Local reservations cover this harness, not unrelated consumption by the
other project sharing the same account. The prepaid provider cap and disabled
auto-reload remain additional controls, with provider enforcement latency as
previously documented. No absolute cross-project spending guarantee is claimed.
