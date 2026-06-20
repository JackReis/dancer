# pai-reasoning — Conventions

> Cross-cutting decisions that apply to all skills in this pack.

## Upstream Credit

All skills in this pack are ported from **PAI v5.0.0** by Daniel Miessler (https://github.com/danielmiessler/PAI). Verbatim originals are vendored at `resources/upstream-verbatim/pai-v5.0.0/skills/` in the =notes vault. Each skill's SKILL.md includes a credit line.

## De-PAI Surgery Checklist

Applied to every ported skill:

1. **DELETE** the "MANDATORY: Voice Notification" section and any `curl localhost:31337/notify` blocks.
2. **REPLACE** `bun run ~/.claude/skills/Agents/Tools/ComposeAgent.ts` with generic Agent dispatch language.
3. **REMOVE** the `~/.claude/PAI/MEMORY/SKILLS/execution.jsonl` log block (telemetry deferred — see below).
4. **REWRITE** absolute `~/.claude/PAI/...` paths to be pack-relative or generic.
5. **KEEP** the prompt body, scientific grounding files, workflow routing tables, and gotchas.
6. **CONVERT** the `USER/SKILLCUSTOMIZATIONS/<Skill>/` override convention into a documented optional pattern.

## Telemetry

The PAI per-skill `execution.jsonl` log block has been **dropped entirely** (YAGNI). Telemetry for skill execution is a deferred follow-up. If needed later, repoint to a dancer-local path rather than resurrecting the PAI path.

## Customization Pattern

PAI's `~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/<Skill>/` override convention is documented as an **optional pattern** in each skill's SKILL.md. Users may place overrides in a skill-customizations directory; if it exists, load and apply preferences. If it doesn't, proceed with defaults. This is not mandatory infrastructure — it's a documented escape hatch.

## Skill-Building Process

Per Jack's CLAUDE.md, the mandatory skill-building process for each skill is:

1. Invoke `superpowers:writing-skills` BEFORE writing
2. Use `plugin-dev:skill-development` for structure
3. Run `skill-reviewer` agent AFTER
4. Test with the plugin-dev harness
5. Gemini review

The PreToolUse `skill-build-gate.sh` hook blocks SKILL.md edits that skip this. This process applies to every skill in this pack.

## Gemini Review

Gemini review verdicts for each skill are recorded below as they complete.

| Skill | Gemini Verdict | Date | Blocker? |
|-------|---------------|------|----------|
| iterative-depth | pending | — | — |

## Overlap Notes

- **RootCauseAnalysis** — scoped as methodology toolkit (5 Whys / Fishbone / Apollo / Swiss Cheese). Description explicitly defers code-bug tracing to `superpowers:root-cause-tracing` and `systematic-debugging`. No duplication.
- **BitterPillEngineering** — cross-links `grill-each-other:dialectic-vocabulary` (over-prompting audit = anti-theatre).
- **FirstPrinciples** — distinct from `superpowers:brainstorming` (FirstPrinciples is deconstruct/challenge/rebuild; brainstorming is divergent ideation).
- **SystemsThinking** — no overlap with existing Jack skills. Clean port.
