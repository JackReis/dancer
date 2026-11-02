# Agent Skills System

**Last Updated:** May 19, 2026
**Current Status:** 5 Jack-authored plugin packs, 27 skills total

## Overview

This repository contains **Jack Reis's own plugin packs** for Claude Code. Originally forked from the Jeremy Longshore marketplace (MIT-licensed), the inherited upstream plugins were removed on 2026-05-16. Dancer now ships only Jack-authored contributions.

## Fleet Directive

All agents working in this repo must follow the **Fleet Directive — Durable Evidence**:
`~/Documents/=notes/docs/conventions/fleet-directive.md`

Done = artifact + path + verification + commit + push + caveats. The evidence, not the vocabulary, is what distinguishes measurement from theatre. Autonomous workers under Arbiter satisfy evidence via `proof_of_work` schema, not handoff files.

## Plugin Packs

| Pack | Category | Skills | Description |
|---|---|---|---|
| `autonomous-ai-agents` v0.4.0 | ai-agency | 3 + 2 MCP bridges | Fleet coordination: identity, hermes-bridge, openclaw-bridge |
| `grill-each-other` v1.3.1 | skill-enhancers | 10 | Dialectic claim discipline: grill-me, peer-grill, fleet-ratify, permutation, etc. |
| `athenaeum` v0.3.0 | skill-enhancers | 5 | Streamlined dialectic: design, reconcile, ratify, audit, arbiter-bridge |
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

- **Total Plugins**: 5
- **Total Skills**: 27
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

## Change Verification

Before changing code, trace direct callers and imports in source and assess affected behavior. Surface material risks before proceeding. Before committing, inspect the diff for unintended changes and run the relevant normal tests and checks.

GitNexus is optional, only when explicitly requested; it is not an editing or commit prerequisite. Do not run it or reindex automatically.
