# Supported model-policy renewal

[SRC] On 2026-10-21 the official Developer API pricing page was read again:
https://ai.google.dev/gemini-api/docs/pricing . Standard/Flex input and output
prices remain Flash3.8 $0.75/$3.75 and $0.375/$1.875 per million tokens;
Lite3.5 $0.30/$2.50 and $0.15/$1.25. Output includes thinking. The Flash3.8
rates have a stated 2026-12-31 promotional end date. No price change is inferred
from successful API access; access metadata does not contain billing rates.

[CODE] `svh.model_policy` independently validates fresh, timezone-aware price
and access reviews. The access record binds exact price-policy bytes. Its
minimum review timestamp continues to enforce both expirations on every paid
reservation. Known rates/model names/tiers and the official pricing URL remain
allowlisted; future rate changes require code review. The metadata probe makes
only authenticated get-model calls, validates both models, archives old evidence
by SHA256, and replaces the active record atomically only on complete success.
No failed provider exception text is emitted. `docs/mvp-usage.md` documents the
operator review and renewal command.

[RUN] Actual authenticated access renewed at 2026-10-21T19:43:15.032268UTC.
Both models return their expected names, generateContent support, 1048576 input
and 65536 output limits. Actual factory construction succeeds for both models
and Standard/Flex, with zero generation requests and unchanged persistent
charges/reservations. Evidence: `notes/runs/model-policy-renewal-smoke.json`.
The original metadata is retained under its content-hash filename.

[RUN/INF] V5 reached policy expiry before its1570 candidate2 launched: that
candidate directory does not exist, the ledger did not advance, and the worker
lock is available. The snapshot under
`notes/runs/m3-standard-submission-v5-policy-expiry-{report,score}.json` retains
all eleven cases: five valid reproduction pairs, four fully passing repairs,
eight considered and three not attempted. The all-case gate remains false.
No new candidate or check version is granted by financial-policy maintenance.
Any continuation must explicitly pin the changed financial module and preserve
that original method and this exact checkpoint. Generation prompts, source
packets, model, tier, thinking level, check limits and test runner remain unchanged.
