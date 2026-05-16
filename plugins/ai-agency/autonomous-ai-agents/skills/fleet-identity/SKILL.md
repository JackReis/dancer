---
name: fleet-identity
description: This skill should be used when the user asks "who is Wings", "who is Zoe", "who runs Kopi", "fleet identity", "fleet mapping", "agent mapping", "identity map", "autonomous ai agent", "what agent is behind X", or needs to look up which runtime agent is behind a Discord/Telegram surface (or vice versa). Returns the canonical mapping from ~/Documents/Coordination/ without duplicating data. Covers Hermes/Wings, OLIVIER_MBP/Zoe, KimiClaw/Mara/Kopi, and any future agents added to the coordination folder.
---

# Fleet Identity Lookup

## Overview

Jack's autonomous-AI-agent fleet separates two things:

- **Runtime agents** — processes on a machine (Hermes, OLIVIER_MBP, KimiClaw, a Claude Code session, etc.)
- **Platform surfaces** — Discord/Telegram bot user accounts that relay messages to/from a runtime agent (Wings, Zoe, Mara, Kopi)

This skill answers "which agent is behind this surface?" (and the reverse) by reading the canonical mapping Jack maintains at `~/Documents/Coordination/`. It never stores data of its own — pure pointer.

## When to Use

User says, or asks:

- "Who is Wings?" / "Who is Zoe?" / "Who runs Mara?" / "Who is Kopi?"
- "What agent runs X on Discord?" / "What surface does Hermes use?"
- "Fleet identity" / "fleet mapping" / "agent mapping" / "identity map"
- "Show me the autonomous AI agent layout"
- Any time a new Claude Code session starts up and needs to understand who's who in the fleet before coordinating

**Do NOT use** for:

- Looking up Discord bot **tokens** or channel routing — that's `dizzy.py` IDENTITIES (a separate primitive). This skill is semantic-intent only.
- Delegating a task to a specific agent — use `hermes mcp serve` for Hermes or `openclaw mcp serve` for OLIVIER_MBP.

## Canonical Data Location

**Source of truth:** `~/Documents/Coordination/*-identity-mapping.md` (most recently modified wins when multiple exist)

**Vault mirror (fallback):** `/Users/jack.reis/Documents/=notes/inbox/agent-coordination.md`

**Do NOT edit either file from within this skill.** Edits happen in the coordination folder directly; the skill just reads.

## Procedure

### Step 1: Find the latest mapping file

```bash
latest=$(ls -t /Users/jack.reis/Documents/Coordination/*identity-mapping*.md 2>/dev/null | head -1)
```

If `$latest` is empty, fall back to the vault mirror:

```bash
fallback="/Users/jack.reis/Documents/=notes/inbox/agent-coordination.md"
```

If BOTH are missing, respond: "No canonical fleet-identity mapping found at `~/Documents/Coordination/` or vault mirror. Check that `Documents/Coordination/<date>-identity-mapping.md` exists. See `~/Documents/Coordination/README.md` for the convention."

### Step 2: Read the mapping file

Use the Read tool. The file has two canonical sections:

- **Intent aliases** — semantic equivalences (e.g., `Hermes = Wings`)
- **Platform identities** — directional routing (e.g., `Hermes → Wings on Discord`)

### Step 3: Filter based on user intent

- If the user asked about a **specific slug** (e.g., "who is Wings"), find the matching row in Platform Identities and return just that pair plus any notes.
- If the user asked for the **full mapping** ("fleet mapping", "identity map", "show me who's who"), return both sections verbatim.
- If the user asked about an **agent** (e.g., "what surfaces does KimiClaw use"), return all rows where that agent appears on either side of the arrow.

### Step 4: Respond with a clear, compact summary

Format example for a slug query ("who is Wings?"):

```
Wings → Hermes

Hermes is the local Hermes Agent (Nous Research runtime) running on
Jack's MacBook Pro (Mac14,9 — Apple M2 Pro, 32 GB); Wings is its
Discord surface.

Source: ~/Documents/Coordination/<latest>-identity-mapping.md
```

For a full-mapping query, return the Intent Aliases + Platform Identities sections as bullet lists, followed by the source path.

### Step 5: Note if the mapping is stale

If the SoT file's `updated:` frontmatter (or mtime) is more than 14 days old, append a soft warning: "Note: the mapping file hasn't been updated in N days — confirm it's still current before acting."

## Current Mapping (snapshot for quick reference)

> Authoritative data lives in `~/Documents/Coordination/`. This snapshot is a cache for fast orientation; always prefer the live read.

**Runtime agents → Discord/Telegram surfaces:**

- Hermes → Wings (Discord)
- OLIVIER_MBP → Zoe (Discord)
- KimiClaw → Mara (Discord)
- KimiClaw → Kopi (Telegram)

**Intent aliases (equivalences):**

- Hermes ≡ Wings
- OLIVIER_MBP ≡ Zoe
- KimiClaw ≡ Mara / Kopi

**Notes:**

- Jack's primary (and currently only) local machine is a **MacBook Pro — Mac14,9, Apple M2 Pro, 32 GB**. Both Hermes and OLIVIER_MBP are local runtimes on this machine; "main Mac" and "the MacBook Pro" refer to the same box until a desktop successor lands.
- Hermes is the local Nous Research Hermes Agent runtime.
- OLIVIER_MBP is the local OpenClaw gateway runtime. The hardware-keyed naming convention forward-prepares for desktop migration: when a Mac mini / Mac Studio lands, the migrated instance becomes OLIVIER_MINI / OLIVIER_STUDIO.
- As of 2026-04-20, Jack is actively evaluating a **Mac mini** or **Mac Studio** as a future desktop. When that machine arrives, one of the runtimes (likely OLIVIER_MBP, which would then be renamed) is expected to move to it — update this note and the coordination mapping at that time.
- KimiClaw is cloud-hosted OpenClaw; its Discord surface is Mara and its Telegram surface is Kopi.
- Dizzy is a separate primitive — `dizzy.py` used by Claude Code sessions for Discord I/O. Not in this mapping because it's a CC-session relay, not a runtime agent of its own.

## Extension — Adding a New Agent

To register a new agent:surface pair (e.g., Jack adds a Gemini CLI local agent with its own Discord surface):

1. Edit `~/Documents/Coordination/<today>-identity-mapping.md` (or create a new dated file — latest-wins glob will pick it up).
2. Add the new row under both **Intent aliases** and **Platform identities** sections.
3. (Optional) Refresh the vault mirror at `=notes/inbox/agent-coordination.md` so OBn has the update.
4. The skill will see the new entry on next invocation — no plugin reinstall required.

## Relationship to Other Primitives

| Primitive | Role | This skill's relationship |
|---|---|---|
| `~/Documents/Coordination/*-identity-mapping.md` | Canonical fleet identity map | **Read only.** SoT. |
| `=notes/inbox/agent-coordination.md` | Vault mirror of the above | **Read fallback.** OBn-indexable. |
| `dizzy.py` IDENTITIES dict | Discord routing (tokens, channels, display names) | **Separate primitive.** This skill does not read/write IDENTITIES. |
| `~/.claude/knowledge-graph.jsonl` | Cross-project entity store | **Not used here.** Identity map lives in the coordination folder, not the KG. |
| `openclaw` MCP (v0.3+) | Delegation bus to OpenClaw gateway | **Delegation, not identity.** Sibling skill `openclaw-bridge`. |
| `hermes mcp serve` (v0.2+) | Delegation bus to Hermes runtime | **Delegation, not identity.** Sibling skill `hermes-bridge`. |

## Troubleshooting

**"No canonical fleet-identity mapping found":** `~/Documents/Coordination/` is either missing or has no `*-identity-mapping.md` file. Check `~/Documents/Coordination/README.md` exists — if yes, recreate the mapping using the 2026-04-20 template. If the whole folder is missing, the coordination convention hasn't been set up on this machine.

**Mapping returns stale data:** The skill picks the most-recently-modified `*-identity-mapping.md`. If edits aren't reflecting, `touch` the file or verify `ls -t` ordering.

**Mirror out of sync with SoT:** Expected — the mirror is human-maintained. Update the vault mirror manually, or point users at the SoT (which this skill prefers anyway).

## File Paths (Absolute)

- Skill: `plugins/ai-agency/autonomous-ai-agents/skills/fleet-identity/SKILL.md`
- Canonical mapping (SoT): `/Users/jack.reis/Documents/Coordination/*-identity-mapping.md` (latest wins)
- Coordination folder README: `/Users/jack.reis/Documents/Coordination/README.md`
- Vault mirror (fallback): `/Users/jack.reis/Documents/=notes/inbox/agent-coordination.md`
- Related routing primitive: `/Users/jack.reis/Documents/=notes/claude/scripts/dizzy.py` (IDENTITIES)
