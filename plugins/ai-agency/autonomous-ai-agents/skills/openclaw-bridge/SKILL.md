---
name: openclaw-bridge
description: This skill should be used when the user asks to "check zoe", "what did zoe say", "ask zoe", "zoe handoff", "openclaw message", "openclaw events", "any pending openclaw approvals", "klawz room", "what's in #bots", "reply via zoe", "zoe says", "send through zolivier", "openclaw bridge", or when Claude Code needs to read/send messages through Zolivier (Zoe) — the OpenClaw side of the fleet's async-messaging substrate. Complements hermes-bridge (Wings side); together they cover the full thinker-fleet messaging surface.
---

# OpenClaw Bridge — Zolivier / Zoe side of the messaging substrate

## Mental model

The fleet has heavy **thinkers** (Claude Code, Gemini CLI, ChatGPT) that work deep on tasks and lose context across session boundaries. **Wings** (Hermes) and **Zoe** (Zolivier/OpenClaw) form a shared **messaging substrate** — they receive messages from Jack's platforms and queue them for thinkers to pick up later.

This skill is Claude Code's interface to **Zoe** (the OpenClaw half). The sibling skill `hermes-bridge` covers Wings. The two skills are not redundant: each routes through a different runtime with a different security profile. Use them together when an operation needs both halves; use one when the destination is single-routed.

## Fleet topology

```
                                 Klawz (Kimi enterprise multi-agent room)
                                ┌───────────────────────────────────┐
                                │  KimiClaw-cloud   (Mara, Kopi)    │
                                │  KimiClaw-desktop (MBP)            │
                                │  KimiClaw-android                  │
                                │  Zolivier (this skill's runtime)   │
                                └────────────┬──────────────────────┘
                                             │
   Jack ─── Discord/Telegram/Slack ──┐       │ insecure relay
                                     │       │ (dev scratchpad)
   Claude Code (heads-down) ─────────┤       │
                                     │       │
   Gemini CLI / ChatGPT ─────────────┤   ┌───┴────────┐
                                     │   │ Zolivier   │
                                     └─► │ (OpenClaw) │
                                         │  on MBP    │
                                         └────────────┘
                                              ▲
                                              │ openclaw mcp serve (this skill)
                                              │
                                          mcp__openclaw__*
```

Key facts:

- Zolivier (Zoe) runs locally on Jack's MacBook Pro. Cloud KimiClaw is a separate runtime that surfaces as Mara on Discord and Kopi on Telegram.
- Three independent KimiClaw memory stores exist (cloud / MBP-desktop / Android). `mcp__openclaw__messages_send` reaches Zolivier only — never any KimiClaw instance directly.
- Klawz is downstream of Zolivier, not upstream. The vault (`=notes`) is SSOT for fleet state; the un-gitted Coordination folder is the whiteboard; Klawz is dev chatter.

## When to use this skill vs. other primitives

| Situation | Use |
|---|---|
| Read/send via Zoe across Discord/Telegram/Slack on Zolivier-managed channels | **This skill** (`mcp__openclaw__*`) |
| Read/send via Wings (Hermes-managed channels) | Sibling skill `hermes-bridge` |
| Approve a pending OpenClaw tool call | **This skill** (`permissions_list_open`, `permissions_respond`) |
| Send a single Telegram DM to Jack (priority notification) | `telegram-messaging` skill (default per user pref) |
| Post to Discord with @-mention fanout / scoped identity prefix | `dizzy.py` directly |
| Look up which runtime is behind a surface ("who is Zoe?") | sibling skill `fleet-identity` |
| Send to the Klawz Kimi room | **No MCP tool** — Klawz posting is currently manual paste (per `06-handoff-drafts.md` pattern) |
| Multi-platform broadcast | Coordinate via Wings + Zoe + dizzy.py — no single fan-out tool exists |

## The 9 OpenClaw MCP tools

Tool calls reach the local OpenClaw gateway via stdio MCP. State lives at `~/.openclaw/`. No network hop at the MCP layer; the gateway WebSocket may reach external services on its own.

| Tool | Purpose |
|---|---|
| `conversations_list` | List active conversations across Zolivier-managed platforms (filterable) |
| `conversation_get` | Detail for one conversation by `session_key` |
| `messages_read` | Read message history for a conversation (chronological, default 50) |
| `messages_send` | **DESTRUCTIVE** — sends a real message via Zolivier. Confirm context first. |
| `attachments_fetch` | Pull non-text attachments from a specific message |
| `events_poll` | Non-blocking check for new events since last poll |
| `events_wait` | Blocking wait for the next event — long-lived watcher use only |
| `permissions_list_open` | List OpenClaw tool calls awaiting approval |
| `permissions_respond` | **DESTRUCTIVE** — approve/deny a pending OpenClaw tool call |

Note: there is no `channels_list` — that tool is Hermes-only. To enumerate channels in OpenClaw, call `conversations_list` and group by the platform/chat-type field.

## Procedure — catch up at a natural stop

1. Call `events_poll` (non-blocking). If empty, skip the rest.
2. For each event, call `conversations_list` (or `conversation_get` if a `session_key` is already known) to find context.
3. Call `messages_read` on the relevant `session_key`.
4. If an attachment is referenced, call `attachments_fetch` with the message_id.
5. Draft the response. Summarize the planned message + reasoning before dispatching.
6. **Run the Klawz scrub** if the destination is a Klawz-routed channel (see Safety section).
7. Call `messages_send` — confirm `session_key`, preview the text.
8. Log the exchange to the session handoff or daily note.

## Procedure — approve a pending tool call

1. Call `permissions_list_open`. If empty, no action.
2. For each pending approval, inspect the requested tool + args.
3. Decide: approve / deny. Justify the decision in one line for the handoff.
4. Call `permissions_respond` with the approval_id and decision.

## Safety — Klawz security boundaries (CRITICAL)

The Klawz Kimi enterprise room is classified **insecure relay + dev scratchpad (asymmetric)**. Zolivier participates in the room. Any `messages_send` whose destination eventually fans out into Klawz must obey these hard rules — re-read this list before each Klawz-bound dispatch:

- **NO secrets, API keys, tokens, credentials.** No `Bearer ...`, no OpenClaw gateway tokens, no Telegram bot tokens, no `export VAR=value` lines.
- **NO PII.** No "Jack Reis" in vault paths, no family names, no addresses, no SSN-adjacent data, no medical details, no financial account numbers.
- **NO absolute filesystem paths containing `jack.reis` or user directories.** Use relative references: `inbox/mara-revival/...` not `/Users/jack.reis/Documents/=notes/inbox/...`.
- **NO URLs with credentials embedded** (`https://user:pass@...`, signed long-lived tokens).

Allowed (explicit allow-list, repeated for clarity):
- Concept-level discussion, design chatter, architecture brainstorming.
- Relative vault paths.
- Published domain names (`oursearanchhome.com`, `k0p1_bot`).
- Public git commit SHAs.
- Fleet-identity callsigns (Mara, Kopi, Zolivier, Neo, Wings, Codex).

Treat ambiguous destinations as Klawz-routed. The cost of an unnecessary scrub is zero; the cost of a leak is permanent.

Source of truth: `~/Documents/Coordination/2026-04-23-klawz-kimi-group-addendum.md`. Vault memory pointer: `~/.claude/projects/-Users-jack-reis-Documents--notes/memory/project_klawz_kimi_group.md`.

## Safety — general

- `messages_send` and `permissions_respond` reach the outside world. Treat them like `git push` — confirm the exact payload before calling.
- Prefer reading before responding when the session context is unfamiliar.
- Avoid `events_wait` inside short-lived task sessions — it blocks. Use `events_poll` for natural-stop catch-up.
- After any `messages_send`, **poll for replies** before declaring delivery complete. Per the `feedback_always_poll_after_send` rule: any outbound fleet message must be followed by polling the same transport for replies. No fire-and-forget.

## Configuration

The `openclaw` MCP server is declared in three places (belt-and-suspenders):

1. **User-scope** (existing): `~/.claude.json` `mcpServers.openclaw` block — picked up by all Claude Code sessions on this machine.
2. **Plugin** (this v0.3 ships): `plugins/ai-agency/autonomous-ai-agents/.claude-plugin/plugin.json` `mcpServers.openclaw` block — portable for marketplace installs.
3. **Vault** (this v0.3 ships): `=notes/.mcp.json` `mcpServers.openclaw` block — survives plugin disable.

Tool calls in this skill resolve to `mcp__openclaw__<tool_name>`.

## Tipi contract

The Tipi `consciousness-interface.json` schema (at `tipi/contract/consciousness-interface.json`) is the upstream coordination contract for the fleet. OpenClaw MCP is the transport layer underneath it for Zolivier-routed traffic. When orchestrating multi-runtime work, prefer the Tipi intent-level abstraction (e.g., `dispatch_hermes` from PT/Neo, sibling intents) over hand-rolled `messages_send` chains. This skill exposes the transport; Tipi is how higher-level coordination should reach for it.

See `=notes/CLAUDE.md` "Tipi as unified coordination contract" + `docs/conventions/multi-session-working-agreements.md §17`.

## Troubleshooting

- **`openclaw mcp serve` fails to start:** check the gateway. `cat ~/.openclaw/openclaw.json` should show server config; `launchctl list | grep openclaw` should list `ai.openclaw.gateway`. If the gateway is down, `launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway`.
- **MCP reports "server down":** restart the Claude Code session — stdio servers spawn per-session. If the issue persists, check `~/.openclaw/logs/`.
- **Empty `conversations_list` despite expecting messages:** the gateway may be running but disconnected from upstream platforms. Check `~/.openclaw/openclaw.json` channel definitions and `openclaw mcp list`.
- **`messages_send` returns 401/403:** gateway credential drift. Check `~/.secrets/openclaw-env.env` (gateway credential file referenced by `ai.openclaw.gateway` plist) for `MISTRAL_API_KEY`, `OPENAI_API_KEY` presence — the 2026-04-22 fleet-config-pii session documented this exact failure mode (see memory `feedback_parser_compat_before_secret_ask`).

## Related

- Plugin plan: `=notes/docs/plans/2026-04-24-autonomous-ai-agent-OpenClaw-MCP-impl.md`
- v0.2 sibling: `=notes/docs/plans/2026-04-24-autonomous-ai-agent-Hermes-MCP-impl.md`
- Parent plan: `=notes/docs/plans/2026-04-20-autonomous-ai-agents-plugin.md` (v0.1)
- Klawz security SoT: `~/Documents/Coordination/2026-04-23-klawz-kimi-group-addendum.md`
- Sibling plugin skill: `hermes-bridge/SKILL.md` (Wings side of the substrate)
- Sibling plugin skill: `fleet-identity/SKILL.md` (who-is-X lookup)
- Vault skill: `=notes/.claude/skills/telegram-messaging/SKILL.md` (preferred for single-Jack DMs per user pref)
