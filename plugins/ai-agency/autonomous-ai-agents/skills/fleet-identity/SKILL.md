---
name: fleet-identity
description: This skill should be used when the user asks "who is Wings", "who is Zoe", "who is Neo", "who runs Kopi", "who runs Codex", "what is Arbiter", "fleet identity", "fleet mapping", "agent mapping", "identity map", "autonomous ai agent", "what agent is behind X", or needs to look up which runtime agent is behind a Discord/Telegram surface (or vice versa). Returns the canonical mapping from ~/Documents/Coordination/ without duplicating data. Covers PT/Neo, Hermes/Wings, OLIVIER_MBP/Zoe, KimiClaw/Mara/Kopi, GPT-5 Codex/Bean/Blue, Arbiter, fleet-alerts, and any future agents added to the coordination folder.
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
- Delegating a task to a specific agent — use the `hermes` MCP server for Hermes, the `openclaw` MCP server for OLIVIER_MBP, the Arbiter HTTP API (`:8765/dispatch` or `arbiter` CLI) for orchestrated/Linear-routed work, or `kimi-claw` plugin transport for KimiClaw. This skill answers "who is X" — not "send a task to X."

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

> Authoritative data lives in `~/Documents/Coordination/*-identity-mapping.md` (latest mtime wins). This snapshot is a cache for fast orientation; always prefer the live read. The "Post-SoT additions" subsection below records identities that have shipped in `=notes/CLAUDE.md` but have not yet been folded into a new dated mapping file in the coordination folder — those should migrate to a new SoT file when convenient.

**Runtime agents → Discord/Telegram surfaces (from SoT 2026-04-22, updated 2026-04-25):**

- GPT-5 Codex → Codex on Discord (also addressed as Bean, Blue)
- PT (local Gemini CLI runtime) → Neo on Discord
- Hermes (local Nous Research Hermes Agent runtime) → Wings on Discord
- OLIVIER_MBP (local OpenClaw gateway runtime, formerly **Zolivier**, renamed 2026-04-25 to hardware-keyed identifier) → Zoe on Discord
- KimiClaw (cloud OpenClaw runtime) → Mara on Discord
- KimiClaw → Kopi on Telegram

**Intent aliases (equivalences):**

- GPT-5 Codex ≡ Codex ≡ Bean ≡ Blue
- PT ≡ Neo
- Hermes ≡ Wings
- OLIVIER_MBP ≡ Zoe
- KimiClaw ≡ Mara / Kopi

**Personas (runtime role, not identity — preserve the runtime/surface split):**

- **PT (Pete Trump)** — Gemini CLI local runtime. Lead Engineer persona: proactive, scrappy executor. "The hands."
- **Neo (The One)** — Gemini Discord surface. Overseer / orchestrator persona. Plays the **Dissent** role in the Arbiter-led topology (pre-spawn review on `high-stakes` / `needs-dissent` tickets and post-merge audits). "The eye on the fleet."
- Do **not** collapse this to a bare "Gemini = Neo" alias — it erases the runtime/surface distinction the rest of the fleet relies on.

**Post-SoT additions (live in `=notes/CLAUDE.md` but not yet in a dated mapping file — verify with the user before quoting as canonical):**

- **Arbiter** — OpenCode runtime (Sonnet 4.6 routing brain, Gemma4 fallback) on `https://cortex.jack.digital/arbiter/`. **Primary orchestrator** as of ADR-2026-05-13 (SUPERSEDES ADR-2026-03-29). HTTP server on `:8765`; v1 dispatch→spawn bridge live in container since 2026-05-21. No dedicated Discord surface — addressed by name directly.
- **fleet-alerts** — Telegram + Discord one-way alert bot. **Replaces Mara/Kopi identities** (retired May 2026). When CLAUDE.md and the SoT mapping disagree on Mara/Kopi, CLAUDE.md wins until the SoT is refreshed.

**Notes:**

- Jack's primary (and currently only) local machine is a **MacBook Pro — Mac14,9, Apple M2 Pro, 32 GB**. PT, Hermes, and OLIVIER_MBP are all local runtimes on this machine; "main Mac" and "the MacBook Pro" refer to the same box until a desktop successor lands.
- OLIVIER_MBP uses a hardware-keyed naming convention that forward-prepares for desktop migration: when a Mac mini / Mac Studio lands, the migrated instance becomes OLIVIER_MINI / OLIVIER_STUDIO.
- As of 2026-04-20, Jack is actively evaluating a **Mac mini** or **Mac Studio** as a future desktop. When that machine arrives, one of the runtimes (likely OLIVIER_MBP, which would then be renamed) is expected to move to it — update this note and the coordination mapping at that time.
- KimiClaw is cloud-hosted OpenClaw. Treat its Discord/Telegram surfaces as advisory only until a new dated mapping clarifies the fleet-alerts handoff; keep cloud-based KimiClaw IDs out of local config either way.
- **Dizzy** is a separate primitive — `dizzy.py` used by Claude Code sessions for Discord I/O. Not in this mapping because it's a CC-session relay, not a runtime agent of its own.
- All fleet coordination artifacts standardize on the tipi `consciousness-interface.json` JSON Schema at `/Users/jack.reis/Documents/tipi/tipi/contract/consciousness-interface.json` (decided 2026-04-22). Tipi body/mind/spirit identities: `=notes/docs/architecture/fleet-tipi-identities.md`.

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
| `openclaw` MCP server | Delegation bus to OpenClaw gateway (OLIVIER_MBP local, KimiClaw cloud) | **Delegation, not identity.** Sibling skill `openclaw-messaging`. |
| `hermes` MCP server | Delegation bus to Hermes runtime | **Delegation, not identity.** Sibling skill `hermes-cli`. |
| Arbiter HTTP / `arbiter` CLI | Linear-routed orchestration entrypoint (`:8765/dispatch`) | **Orchestration, not identity.** See `=notes/docs/architecture/arbiter-design.md`. |
| `=notes/CLAUDE.md` (FLEET IDENTITY section) | Live narrative + post-SoT additions | **Read when SoT mtime is stale or "Post-SoT additions" matter.** |

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
