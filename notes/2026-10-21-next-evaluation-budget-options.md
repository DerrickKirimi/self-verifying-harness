# Reviewed options for the next development evaluation

[SRC] Reviewed2026-10-21. The official
[Flex generate-content guide](https://ai.google.dev/gemini-api/docs/generate-content/flex-inference)
documents half-price inference, supported3.5FlashLite/3.8Flash models,
`service_tier=flex`, no automatic server upgrade to Standard, and longer client
timeouts for queued requests. [INF] This is a candidate for another sequential
evaluation under the same $4 ledger cap and full-context reservations. It has
**now been implemented and called** in the separately frozen v3 method below. Keep retries and client fallback disabled;
unknown outcomes must still retain reservations.

[SRC] The official [pricing table](https://ai.google.dev/gemini-api/docs/pricing)
lists3.5FlashLite Flex at input$0.15/M and output$1.25/M including thinking.
The [thinking guide](https://ai.google.dev/gemini-api/docs/thinking) lists medium
as supported for that model. [INF] A new prospective method could combine that
tier/effort with corrected root-spec reference imports. Do not silently change
the completed v2 run or its rubric, and do not raise/reset the cap.

[CODE] Installed google-genai2.31.0 exposes GenerateContentConfig.service_tier;
the budget wrapper now validates factory-owned tiers, matching dated prices,
full-input/output worst-case reservations, a 900-second Flex timeout and bind/config
overrides. No retry or Standard fallback is enabled. [RUN] Actual access passed:
`notes/runs/gemini-flex-smoke.json`, six input tokens and one output token,
$0.000003 local accounted cost. This is transport evidence, not code performance
or a provider billing receipt. Reviewed policy: `notes/runs/gemini-flex-policy.json`.

[CODE/INF] `evals/m3-method-mapped-flex-v3.json` freezes a separate all-eleven
development evaluation before its calls: Lite/Flex/medium, mapped base-spec
import examples and explicit recorded-transition fidelity. Actual generated
checks remain unchanged. The two-distinct-version limit, rubric, denominator,
SDK-owned loop and $4 cap are unchanged; old v1/v2 successes are not pooled.

[SRC] The [countTokens reference](https://ai.google.dev/api/tokens) accepts an
overall generateContentRequest, including system/tool input. Its text example
shows count10 versus generation prompt usage11. The
[billing FAQ](https://ai.google.dev/gemini-api/docs/billing) calls a counting API
GetTokens unbilled but does not name that REST method explicitly.
[INF] No complete counted-to-billable upper-bound relation was established in
this review. Do not replace full-context safety reservations with token estimates
or assume that preflight count alone bounds spend.
