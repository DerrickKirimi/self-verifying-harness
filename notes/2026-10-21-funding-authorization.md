# Additional owner-authorized evaluation funding

[SRC] On2026-10-21 the owner explicitly reported a new prepaid balance of$11.51,
auto-renew off and project monthly usage/limit of$2.69/$12.00, then instructed
"proceed". These are owner-reported figures, not an independently fetched
provider receipt. No billing/account settings are changed by the harness.

[RUN/INF] Before funding, the local ledger retains$3.693868 estimated settled
cost plus$0.167527 uncertain reservation, total$3.861395. Set the **cumulative
local limit to$12.00**, preserving all records and that uncertain reservation.
This permits at most$8.138605 more reserved/charged usage, below both the
reported$9.31 monthly headroom and$11.51 prepaid balance. The provider headroom
buffer is$1.171395. Do not interpret a fresh balance as a ledger reset.

[CODE] `svh authorize-budget` requires an explicit non-secret authorization
reference and expected previous cap, records an idempotent funding event, and
refuses stale amounts or re-enabling an unexpected-overage lock. Configuration
alone still cannot raise an existing ledger. `svh budget` opens the existing
limit without tightening it back to the original default. An uncertain provider
error is not automatically refunded by this operation.

[INF] Next evaluation uses a separately frozen stronger-model method. Preserve
all earlier runs and their unsuccessful gates; no pooling of old successes.
