# CLAUDE.md

All project instructions live in `AGENTS.md`, so every harness reads the same file. It's imported here:

@AGENTS.md

## Claude Code specifics

- Read `STATUS.md` at the start of a session and update it before you stop.
- Use the session scratchpad only for throwaway output. Anything another agent might need goes in the repo (`notes/`, `docs/`, `STATUS.md`).
- Load deferred tools in one batched search. Don't spawn subagents unless the owner asks.
- Commit messages end with the attribution line your harness instructions specify.
