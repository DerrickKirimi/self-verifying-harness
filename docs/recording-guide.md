# Record the first three walkthroughs

The fixture app uses fictional data only. The pre-fix commit is
`426a532c59194764244a8635781f28a1ac41a8df`; the post-fix commit is
`eee15ebbb2e6a06419bbca30899e589ad644fb30` (`evals/fixtures.json`). [CODE]
Both versions use the same HTTP handler for the browser table and API checks.
The pytest checks verify the HTTP data, not browser interactions or rendering. [CODE]

## Start the app

From the repository root:

```sh
uv sync --locked
docker build -t svh-eval:local sandbox
uv run svh serve --revision pre
```

Open `http://127.0.0.1:8080`. Stop with Ctrl+C. To inspect the fixed version,
restart with `uv run svh serve --revision post`. The app runs in Docker with
only the archived fixture mounted read-only. The recording server publishes a
loopback port on Docker's default bridge; the oracle containers instead have no
external network. [CODE]

## Three clips

Use your own voice, record only this browser window, and keep unrelated tabs,
notifications and account details off screen. Save clips under the gitignored
`evals/recordings/` directory. These are recording instructions, not observations. [INF]

| Clip | Actions on the pre-fix app | Expected behaviour to explain | Reproduction |
|---|---|---|---|
| `search-case.webm` | Show the Login issue; enter `login` in Search titles and submit | Searching should ignore case and find the Login issue | `test_search.py` |
| `closed-filter.webm` | Click All, then Closed | Closed should show only Export is slow | `test_closed.py` |
| `priority-order.webm` | Click All, then Priority | Priorities should appear high, medium, low | `test_priority.py` |

Say what happened and what you expected while demonstrating it. You can use
different words; annotations must describe what was actually said and shown.
We have not recorded any clips on your behalf. [CODE]

## Annotate actual evidence

Create one JSON file per clip under `evals/annotations/`, following
`evals/schema/walkthrough.schema.json`. Record the real duration, actual claim
start/end timestamps, your speaker label, both full commit IDs above, and the
matching reproduction path. Use `"repo": "."`, `"bug_origin": "planted"`,
`"kind": "bug"` and `"runner": "pytest"` for these fixtures. Omit `observed`:
those fields belong to the eventual annotated-walkthrough runner. [CODE]

```sh
uv run svh validate evals/annotations/search-case.json
uv run svh verify
```

`validate` checks schema, timestamps, containment and file existence. It does
not decode the media, verify spoken content, inspect commit contents or trust
hand-entered `observed` values as oracle evidence. `verify` currently verifies
the three fixtures from `evals/fixtures.json`; it does not yet attach results to
annotations or count them as completed M0 walkthroughs. [CODE]

M0 still requires 10–20 recorded, annotated bugs and observed failing/passing
reproductions for all of them (`docs/roadmap.md`). The first three are the initial
checkpoint; retrieval and model selection follow the completed M0 gate. [SRC]
