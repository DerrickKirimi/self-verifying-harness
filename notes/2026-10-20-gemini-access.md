# Gemini access and budget preparation

[SRC] The owner authorized reusing the separate project's Gemini credentials
and supplied prepaid billing evidence with auto-reload disabled. Credentials
remain in the original external secret file; a gitignored local configuration
points to it. No key bytes or billing screenshots belong in commits.

[CODE/RUN] `svh.budget` provides persistent, atomic request reservations. Five
tests exercise rounding, concurrency, ambiguous outcomes, restarts, idempotent
settlement and unexpected overages. Total runner suite: 49 passed. No model
transport or metered generation has been run. This is preparation for authorized
spending, not ingestion work before M0 admission.

[SRC] Primary Google documentation checked 2026-10-20:

- [Model catalog](https://ai.google.dev/gemini-api/docs/models): lists
  `gemini-3.8-flash` and `gemini-3.5-flash-lite` for new projects.
- [Pricing](https://ai.google.dev/gemini-api/docs/pricing): standard Flash 3.8
  input $0.75 / million tokens, output including thinking $3.75 / million through
  2026-12-31; listed increases from 2027-01-01. Flash-Lite 3.5 standard input
  $0.30 / million for text/image/video/audio, output including thinking $2.50.
- [Billing](https://ai.google.dev/gemini-api/docs/billing/): prepaid balance and
  project spending-cap enforcement have latency. Provider limits alone cannot
  guarantee no overrun.

[INF] These are candidate rates, not measured model quality or authenticated
availability. At M1, confirm model access and current prices again, bind request
upper bounds to token limits, disable paid optional tools and automatic retries,
and record actual input/output/thinking usage before settling a reservation.
Unknown outcomes must retain their full reservation. The local cap includes a
buffer below the supplied balance but cannot account for unrelated concurrent
consumption of the shared account.
