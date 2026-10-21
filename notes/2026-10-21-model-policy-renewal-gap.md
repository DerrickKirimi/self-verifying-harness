# Release audit: reviewed model policy renewal

[CODE] `scripts/probe_gemini.py` reads authenticated metadata, but writes a fresh
`checked_at` together with hardcoded `pricing_checked_date=2026-10-20`.
`configured_model` requires both dates to agree and also pins that pricing date
in code. `Price.validate` rejects metadata older than24 hours. Consequently,
running the probe on a later day is not a working renewal procedure: it produces
metadata that the factory rejects. Changing only a timestamp would also be
unacceptable evidence of a pricing/access recheck.

[INF] Before declaring the MVP shipped, provide a supported renewal procedure:
actually reread official prices, fetch authenticated model limits/actions, bind
the reviewed rates/date/source and reject stale or incompatible policies. It
must not depend on editing a historical review date or silently renewing trust.
Keep the same cumulative ledger, full-context reservations, no retries/fallback
and owner-only credential handling. Document the command and test its failure
paths without making paid generation calls.

[RUN/INF] The current metadata remains usable until2026-10-21T18:22:00UTC under
the24-hour rule; its original checked time is2026-10-20T18:22:00.129013UTC.
Do not run the old probe or edit pinned `gemini.py` while the v5 evaluation is
using its frozen method. Resolve renewal after that run, then test the actual
factory using genuinely refreshed metadata. The no-model README replay is
independent of this expiration.
