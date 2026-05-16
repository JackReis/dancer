# Agent Skills System

**Last Updated:** May 16, 2026
**Current Status:** 4 Jack-authored plugin packs, 21 skills total

## Overview

This repository contains **Jack Reis's own plugin packs** for Claude Code. Originally forked from the Jeremy Longshore marketplace (MIT-licensed), the inherited upstream plugins were removed on 2026-05-16. Dancer now ships only Jack-authored contributions.

## Plugin Packs

| Pack | Category | Skills | Description |
|---|---|---|---|
| `autonomous-ai-agents` v0.4.0 | ai-agency | 3 + 2 MCP bridges | Fleet coordination: identity, hermes-bridge, openclaw-bridge |
| `grill-each-other` v1.2.0 | skill-enhancers | 9 | Dialectic claim discipline: grill-me, peer-grill, fleet-ratify, etc. |
| `leonardo` v1.1.0 | ai-agency | 1 | Protected-string decoder with Discord audit |
| `pocock-engineering` v1.0.0 | skill-enhancers | 8 | SDLC skills forked from Matt Pocock's framework |

## 2025 Schema Compliance

All Dancer-packaged skills follow the 2025 schema. The portable minimum across Superpowers, user skills, vault skills, and package-installed skills is `name` plus `description`; `allowed-tools`, `version`, plugin manifests, commands, hooks, and MCP entries are adapter/package fields unless a target runtime explicitly requires them.

### Dancer Package Fields

```yaml
---
name: skill-name                    # lowercase, hyphens, max 64 chars
description: |                      # Clear "what" and "when", max 1024 chars
  What this skill does and when to use it.
  Include trigger phrases like "analyze performance" or "optimize code"
  so users know when this skill will activate.
allowed-tools: Read, Write, Bash    # Dancer package/runtime field
version: 1.0.0                      # Dancer package/runtime field
---
```

## Current Metrics

- **Total Plugins**: 4
- **Total Skills**: 21
- **Schema Compliance**: 100%

## Plugin Developer Guide

### Adding Skills to Your Plugin

1. Create skill directory: `plugins/<category>/<pack-name>/skills/<skill-name>/`
2. Create SKILL.md with 2025 schema frontmatter
3. Validate: `python3 scripts/validate-skills-schema.py`
4. Test locally with plugin
5. Add entry to `.claude-plugin/marketplace.json` and `marketplace.extended.json`

### Best Practices

1. **Clear Trigger Phrases**: Include 3-5 example phrases in description
2. **Minimal Tool Set**: Only request tools you actually need
3. **Version Tracking**: Increment version on updates (semantic versioning)
4. **Step-by-step Workflows**: Break complex tasks into phases
5. **Real Examples**: Include actual usage scenarios

## Resources

- **Repository**: https://github.com/JackReis/dancer

## Repository Remote Policy
- Repo policy: GitHub is primary `origin` and CI/CD source; GitLab is backup remote (`gitlab`) with GitLab CI disabled.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **dancer** (101360 symbols, 102995 relationships, 114 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/dancer/context` | Codebase overview, check index freshness |
| `gitnexus://repo/dancer/clusters` | All functional areas |
| `gitnexus://repo/dancer/processes` | All execution flows |
| `gitnexus://repo/dancer/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
