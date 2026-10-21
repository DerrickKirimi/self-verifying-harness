# Browser feedback during reproduction development

[RUN/INF] The earlier `generated-v1` run is an incomplete development run, not an
all-case result. One task (1679) is fully generated/verified/exported with real
Harbor rewards0/1. Four other cases exhaust their final candidate budgets; 1610
also fails (the cheaper model first omits required media calls, then selects an
invalid root). 1557 is explicitly abstained without inventing an expected policy.
Four cases remain unattempted in that old run. All are retained in its denominator.

[CODE/INF] The important harness improvement is **runtime feedback before final
submission**. The model can call `probe_browser_check` from the existing
SDK-owned loop. The controller freezes each submitted version and runs it on a
fresh BUGGY checkout, returning real setup/assertion errors. The model cannot
edit source or choose image/commit/runner arguments. Every executed version is
retained, and the original two-distinct-check-version limit remains enforced
across both final candidate slots. Repeated observations do not create new check
versions. Setup errors, timeouts and initial-state assertions do not authorize a
source fix; the controller still reviews the actual target failure separately.

[CODE] Typed final submission is unavailable until the probe actually returns a
completed assertion failure. It references a probe ID; canonical test bytes are
copied exactly from that frozen model-authored probe, avoiding a second code copy.
The final controller reobserves those unchanged bytes independently before any
source fix. Source fixes and native regressions still execute in fresh containers.
There is no added model loop: deepagents owns every read/probe/final decision.

[CODE/RUN] Actual metadata and three bounded PNG frames are now fetched through
MCP before model invocation and supplied as image input. Thus the model cannot
skip the recording simply by calling its final-output tool prematurely. Public
cases still have no audio; narrated-input quality is not inferred from these clips.
New integrity units cover media delivery, write denial, probe version limits and
final-tool gating; eleven targeted checks pass with required asynchronous loopback
permissions. No extra paid probe was used to test these mechanics.

[INF] A fresh development run, `probed-v2`, is prepared on the SAME frozen eleven
artifacts with unchanged acceptance rubric. Method is fixed before its first
model call in `evals/m3-method-probed-v2.json`: Gemini3.5FlashLite/low, 8192 output
cap, 30 graph steps, two distinct executed versions per case, explicit AI-assisted
review. Do not combine a v1 case outcome with a v2 case outcome to inflate a rate.
This remains development-set iteration, not independent held-out evaluation.
The existing v1 verified task remains valid regardless of v2 outcomes.

[RUN] Before the fresh run, the shared guard ledger is $3.141581 settled estimate,
$0.858419 available, zero unsettled requests, unchanged $4 cap. No resetting,
raising or duplicating workers. The cheaper model leaves enough reservation
headroom for a complete stage; the larger model's full-context reservation would
otherwise stop a stage partway through the remaining budget.
