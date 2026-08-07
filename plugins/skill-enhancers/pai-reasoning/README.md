# pai-reasoning

> Structured reasoning skills adapted from PAI v5.0.0.

## Pack contents

| Skill | Description |
|-------|-------------|
| iterative-depth | 2-8 lens passes to extract ISC criteria invisible from any single angle |
| first-principles | Physics-style deconstruct/challenge/rebuild from fundamentals |
| systems-thinking | Iceberg, causal loops, Meadows leverage points, systems archetypes |
| root-cause-analysis | 5 Whys / Fishbone / Apollo / Swiss Cheese for non-code failures |
| bitter-pill-engineering | Over-prompting audit — would a smarter model make this rule unnecessary? |
| science | The scientific method as universal problem-solving cycle |
| aperture-oscillation | 3-pass scope oscillation (tactical vs strategic) to surface design tensions |
| ideate | Multi-cycle evolutionary ideation engine with 9 phases |
| be-creative | Single-pass divergent ideation via Verbalized Sampling |
| world-threat-model | 11-horizon (6mo-50yr) stress-testing of ideas against future scenarios |
| evals | Not ported — see CONVENTIONS.md for decision rationale |

## De-PAI process

All skills were de-PAI'd from PAI v5.0.0 sources following the standard surgery checklist:
- Removed voice notification curl blocks (localhost:31337)
- Removed ComposeAgent.ts / bun run references (replaced with Agent(subagent_type=...) dispatch)
- Removed execution.jsonl logging
- Removed ~/.claude/PAI/ customization paths
- Rewrote all paths to be pack-relative

## Conventions

See `CONVENTIONS.md` for the full de-PAI surgery checklist, overlap table with existing Jack skills, and tier-2 skill decisions.

## Attributions

All skills credit PAI v5.0.0 (Daniel Miessler, MIT-licensed) in their SKILL.md files. Verbatim originals are preserved at `=notes/resources/upstream-verbatim/pai-v5.0.0/skills/`.
