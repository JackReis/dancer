# pai-reasoning Conventions

> How PAI v5.0.0 reasoning skills were adapted for Jack's fleet.

## De-PAI surgery checklist (applied to every skill)

1. Delete the customization block pointing to `~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/<Skill>/`.
2. Delete the "MANDATORY: Voice Notification" section and its `curl http://localhost:31337/notify` block.
3. Delete the execution-log JSONL block that appends to `~/.claude/PAI/MEMORY/SKILLS/execution.jsonl`.
4. Replace `bun run ~/.claude/skills/Agents/Tools/ComposeAgent.ts` with generic `Agent(subagent_type=...)` dispatch language.
5. Rewrite absolute `~/.claude/...` paths to be pack-relative or generic.
6. Keep the prompt body, scientific grounding files, workflow routing tables, and gotchas.
7. Convert skill names to kebab-case for the dancer pack (`IterativeDepth` -> `iterative-depth`).

## Runtime coupling we do NOT introduce

The following strings must NOT appear in adapted SKILL.md files:

- `localhost:31337`
- `ComposeAgent.ts`
- `MEMORY/SKILLS`
- `~/.claude/PAI/`

Verification:

```bash
cd /Users/jack.reis/Documents/dancer
grep -rIE 'localhost:31337|ComposeAgent\.ts|MEMORY/SKILLS|~/.claude/PAI/' plugins/skill-enhancers/pai-reasoning/skills/
# Expected: no output
```

## Customization convention

PAI's per-skill `SKILLCUSTOMIZATIONS/` override directory is not implemented. If a user wants to customize a skill, they should fork the SKILL.md in their local skill path or open a PR.

## Telemetry convention

PAI's per-skill `execution.jsonl` logging is dropped (YAGNI). If runtime telemetry is needed later, it will be implemented as a single cross-cutting hook in the runtime, not per-skill log blocks.

## Overlap with existing Jack skills

| pai-reasoning skill | Existing Jack skill | Relationship |
|---|---|---|
| root-cause-analysis | superpowers:root-cause-tracing | PAI skill = non-code RCA methodology; superpowers = live code-bug tracing. Explicit deferral in description. |
| bitter-pill-engineering | grill-each-other:dialectic-vocabulary | Cross-link; both target unexamined claims / theatre. |
| science | (none) | Standalone scientific method meta-skill. |
| aperture-oscillation | (none) | Standalone tactical/strategic scope analysis. |
| ideate | superpowers:brainstorming | Ideate = multi-cycle evolutionary system; brainstorming = collaborative interactive design refinement. Separate skills, distinct purposes. |
| be-creative | (none) | Standalone single-pass divergent ideation. |
| world-threat-model | (none) | Standalone long-term risk analysis harness. |
| evals | (not ported) | Documented as covered by existing Paperclip/Hermes eval tooling. See evals/SKILL.md for decision rationale. |

## Tier-2 skill decisions

| PAI skill | Decision | Rationale |
|---|---|---|
| ApertureOscillation | Ported as aperture-oscillation | No Jack analog. Clean port. |
| Science | Ported as science | No Jack analog. The universal algorithm meta-skill. |
| Ideate | Ported as separate skill | Multi-cycle evolutionary system; distinct from brainstorming and be-creative. |
| BeCreative | Ported as separate skill | Single-pass divergent; distinct from ideate. Per PAI's own framing ("This is NOT Ideate"). |
| Evals | NOT ported (doc-only) | Jack's existing eval tooling (Paperclip verifiers, Hermes model reviews, bd task tracking) covers all PAI Evals capabilities. Duplicate would add scaffolding. |
| WorldThreatModel | Ported as world-threat-model | No Jack analog. 11-horizon stress-testing harness. |

## Review log

| Date | Reviewer | Verdict | Notes |
|---|---|---|---|
| 2026-06-26 | — | — | Scaffold created; skills pending. |
| 2026-08-06 | Coordinator | PASS | All Plan 2 skills ported; bitter-pill-engineering SKILL.md added; tier-2 skills ported; evals not ported (covered by existing tooling); Plan 3 Council+RedTeam ported as new grill-each-other skills; thinking-capability-vocabulary.md updated. |
