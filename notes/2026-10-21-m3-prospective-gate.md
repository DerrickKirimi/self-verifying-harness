# M3 prospective measurement

[CODE/INF] `evals/m3-rubric.json` instantiates the unchanged M3 acceptance in
`evals/PROTOCOL.md`, before any generated reproduction or repair. At least ten
artifacts, Wilson lower bound >=0.20 for valid generated fail/pass reproductions,
and at least one generated repair passing independent native regressions.
All eleven frozen cases remain in the denominator, including ambiguity and
budget exhaustion. Maximum two check candidates per case; every changed check
needs a fresh observed base assertion failure before a source fix is attempted.

[CODE] `svh.verification` separates reproduction and repair rates. It rejects
runtime errors, incomplete browser suites, skips, timeouts, changed check hashes,
different environments and changed test identities. The controller stages only
check bytes in a fresh base sandbox; source fixes may transfer only bounded
`lib/**/*.js` contents, independent of agent-modifiable git state.

[INF] The first browser adapter uses the application's native Karma/Chrome
infrastructure because its assertions can inspect actual rendered DOM and
modeling services. This is a deliberate application adapter, not a new agent
loop; deepagents still owns generation. Generic Playwright/pytest adapters remain
future additions. A trivial failing assertion smoke validates runner plumbing
only and never counts as a recording-derived reproduction.
