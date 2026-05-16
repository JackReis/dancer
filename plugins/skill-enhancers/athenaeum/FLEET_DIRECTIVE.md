# Fleet Directive — Durable Evidence

> You are not alone in this codebase. Other agents and humans read these files
> in parallel, across machines, across days.

## Core rule

Done = artifact + path + verification + commit + push + caveats.

If the next observer cannot find it, the agent did not finish it.

## Required evidence

Every completion must include:

1. **Artifact** — what changed (file, commit, function, config key, rendered output).
2. **Path** — where it lives (absolute path, repo-relative path, or commit SHA).
3. **Verification** — the exact command or check performed and the observed result.
4. **Commit + push** — committed to git AND pushed to the remote. Not pushed = not durable.
5. **Caveats** — what was NOT done, what could still fail, what assumptions you made.

## Agent-specific compliance

- **Human-attended sessions** (Claude Code, Cursor, Gemini CLI, Codex): Write evidence to the repo/vault directly. Handoff files are acceptable for inter-session coordination.
- **Arbiter autonomous workers**: Satisfy the evidence requirement via the `proof_of_work` schema (`pr_url`, `files_changed`, `caveats`, `test_results`). Handoff files are not required for isolated worker runs.
- **All agents:** Verification must come from running the thing, not from reading the diff. You cannot observe yourself and call it measurement.

## Final standard

Durable or it did not happen.

---

*This directive is a companion to the Athenaeum skill pack. Full alignment audit: see `fleet-reports/2026-05-16-fleet-directive-alignment-report.md`.*
