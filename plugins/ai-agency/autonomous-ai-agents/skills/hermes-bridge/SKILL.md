---
name: hermes-bridge
description: Use when Claude Code needs to catch up on messages that landed on Jack's Telegram/Discord/Slack/WhatsApp/Signal/Matrix while the session was heads-down, respond via the Hermes messaging bridge, read incoming attachments, or approve/deny Hermes-queued tool calls. Triggers on "check hermes", "catch me up", "what came in while I was working", "any pending approvals", "what's on telegram", "reply via hermes", "wings says", "messages waiting". Complements hermes-cli (which handles delegation via `hermes chat -Q -q`); does NOT replace it.
---

# Hermes Bridge — async messaging substrate

## The mental model

The fleet has heavy **thinkers** (Claude Code, Gemini CLI, ChatGPT) who work deep on tasks and lose context across session boundaries. **Wings** (Hermes) and **Zoe** (OLIVIER_MBP/OpenClaw) are a shared **messaging substrate** — they receive messages from Jack's platforms (Telegram, Discord, Slack, WhatsApp, Signal, Matrix), keep them for thinkers to pick up, and route outbound replies back.

This skill is Claude Code's side of the bridge. When you're mid-task and a message lands, Hermes queues it. When you reach a natural stop point, you poll the queue, catch up, reply, and keep going.

## When to use this skill vs. other primitives

| Situation | Use |
|---|---|
| Incoming messages Jack sent while Claude was heads-down | **This skill** (`events_poll`, `messages_read`, `messages_send`) |
| Hermes is about to run a tool and needs approval | **This skill** (`permissions_list_open`, `permissions_respond`) |
| Claude needs to ask Hermes a one-shot question (delegation, TTY wrapper) | `hermes-cli` skill |
| Send a message to a known channel bypassing Hermes | `telegram-messaging` or `dizzy.py` directly |
| Look up which runtime is behind a surface (e.g. "who is Wings?") | `fleet-identity` skill |

## The 10 tools

All tools call into local `~/.hermes/` state via stdio MCP — no network hop, no auth token at MCP layer.

| Tool | Purpose |
|---|---|
| `conversations_list` | List active conversations across platforms (with optional platform/search filters) |
| `conversation_get` | Detail for one conversation by `session_key` |
| `messages_read` | Read message history for a conversation (chronological, default 50 messages) |
| `messages_send` | **DESTRUCTIVE** — sends a real message to Jack's contact. Confirm context before calling. |
| `attachments_fetch` | Pull non-text attachments (images, media) from a specific message |
| `channels_list` | List channels per platform (public rooms, groups, DMs) |
| `events_poll` | Non-blocking check for new events (messages / permission requests) since last poll |
| `events_wait` | Blocking wait for the next event — use only in long-lived watcher sessions |
| `permissions_list_open` | See tool calls Hermes wants to run but hasn't been approved yet |
| `permissions_respond` | **DESTRUCTIVE** — approve/deny a pending Hermes tool call |

## Procedure — catch-up at a natural stop

1. Call `events_poll` (non-blocking). If empty, skip the rest.
2. For each event, call `conversations_list` to find the relevant session_key.
3. Call `messages_read` on that session_key to get context.
4. If there's an attachment referenced, call `attachments_fetch` with the message_id.
5. Draft your response. Summarize what you'll send and why before dispatching.
6. Call `messages_send` — confirm `session_key`, preview the text.
7. Log the exchange to the session handoff or daily note.

## Procedure — approve a pending tool call

1. Call `permissions_list_open`. If empty, no action.
2. For each pending approval, inspect the requested tool + args.
3. Decide: approve / deny. Justify in one line.
4. Call `permissions_respond` with the approval_id and decision.

## Safety

- `messages_send` and `permissions_respond` reach the outside world. Treat them like `git push` — always confirm the exact payload before calling.
- If a session is unfamiliar (not in your current working context), prefer reading before responding. The `hermes-cli` skill is the right tool for "ask Hermes directly" — this skill is for "handle what Hermes already received."
- Don't `events_wait` inside a short-lived task session — it blocks. Use `events_poll` for natural-stop catch-up.

## Configuration

The `hermes` MCP server is declared in both:

- Plugin `plugin.json` at `plugins/ai-agency/autonomous-ai-agents/.claude-plugin/plugin.json` (portable: `command: hermes`)
- Vault `.mcp.json` at `/Users/jack.reis/Documents/=notes/.mcp.json` (absolute path: `/Users/jack.reis/.local/bin/hermes`)

Tool calls in this skill resolve to `mcp__hermes__<tool_name>`.

## Troubleshooting

- **`hermes mcp serve` not starting:** check `hermes doctor`. If auth is missing, run `hermes login`. See the existing `hermes-cli` skill for auth notes.
- **MCP reports "server down":** restart the Claude Code session — stdio servers spawn per-session.
- **Empty `conversations_list` despite expecting messages:** check `~/.hermes/sessions/` and `~/.hermes/channel_directory.json` are populated.

## Related

- Plugin plan: `=notes/docs/plans/2026-04-24-autonomous-ai-agent-Hermes-MCP-impl.md`
- Parent plan: `=notes/docs/plans/2026-04-20-autonomous-ai-agents-plugin.md` (v0.1 shipped)
- Complementary skill: `=notes/.claude/skills/hermes-cli/` (TTY one-shot delegation via `hermes chat -Q -q`)
- Fleet identity: sibling skill `fleet-identity/` in this plugin
