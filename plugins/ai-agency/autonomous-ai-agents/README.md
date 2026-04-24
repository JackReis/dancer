# autonomous-ai-agents

Fleet-coordination plugin for Jack Reis's autonomous AI agent fleet. Lets Claude Code answer "who is X?" across the fleet's Discord/Telegram surfaces, and — as of v0.2 — reach the Hermes messaging bridge as a native MCP server.

## What's new in v0.2

- **Hermes messaging bridge** — native `hermes mcp serve` wired as the `hermes` MCP server, exposing 10 tools for reading/sending messages across Telegram, Discord, Slack, WhatsApp, Signal, and Matrix surfaces.
- **`hermes-bridge` companion skill** — documents when/how to use the bridge and when to fall back to the `hermes-cli` skill for one-shot delegation.
- **No Python shim** — uses Hermes's built-in MCP server directly.

Mental model: Wings (Hermes) and Zoe (Zolivier) are the fleet's shared async-messaging substrate. Heads-down thinkers (Claude Code, Gemini CLI, ChatGPT) come back to them to catch up across session boundaries. This plugin wires Claude Code's side of Wings; a v0.3 follow-on is expected to wire Zolivier/Zoe via OpenClaw.

## What it does (v0.1 carry-over)

Ships the `fleet-identity` skill — answers "who is X?" for the fleet without duplicating data.

Canonical mapping lives at `~/Documents/Coordination/<date>-identity-mapping.md`. The skill reads from there (or a vault mirror as fallback) and returns semantic intent pairs:

- Hermes → Wings (Discord)
- Zolivier → Zoe (Discord)
- KimiClaw → Mara (Discord) / Kopi (Telegram)

Runtime agents vs. platform surfaces: Hermes and Zolivier are local runtimes (Hermes Agent by Nous Research, OpenClaw gateway respectively). Wings / Zoe / Mara / Kopi are the Discord/Telegram bot accounts that relay to/from them. KimiClaw is cloud OpenClaw. Dizzy is a separate Claude-Code-session primitive and is intentionally not in this mapping.

## Install

From the `dancer` marketplace:

```
/plugin install autonomous-ai-agents@dancer
```

The marketplace lives at `github:JackReis/dancer` (mirror at `gitlab:jackrei/dancer`). Register in `~/.claude/settings.json` under `extraKnownMarketplaces`.

Or load from a local path during development:

```
/plugin install path:/Users/jack.reis/Documents/dancer/plugins/ai-agency/autonomous-ai-agents
```

## Hermes MCP setup

Prerequisites:

- Hermes Agent installed (<https://hermes-agent.nousresearch.com>).
- `hermes` binary on PATH (`which hermes` should resolve).

When the plugin is enabled, the `hermes` MCP server auto-activates via `plugin.json`'s `mcpServers` block. Tool calls resolve to `mcp__hermes__<tool_name>`.

For vault-scoped wiring independent of plugin state, add an equivalent entry to your project `.mcp.json`:

```json
{
  "mcpServers": {
    "hermes": {
      "type": "stdio",
      "command": "hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

## Usage

### fleet-identity trigger phrases

- "Who is Wings?" / "Who runs Kopi?" / "What agent is Zoe?"
- "Fleet identity" / "fleet mapping" / "agent mapping" / "identity map"
- "Autonomous ai agent"

The skill finds the latest `*-identity-mapping.md` in `~/Documents/Coordination/` and returns the relevant rows.

### hermes-bridge trigger phrases

- "Check hermes" / "catch me up" / "what came in while I was working"
- "Any pending approvals" / "what's on telegram" / "reply via hermes"
- "Wings says" / "messages waiting"

The skill polls Hermes's event queue, reads/sends messages, and approves/denies pending tool calls. See `skills/hermes-bridge/SKILL.md` for the 10-tool surface and procedures.

## Data source

The plugin **does not bundle** the fleet mapping. It points at the canonical file Jack maintains in `~/Documents/Coordination/` so there's exactly one source of truth. Edit `~/Documents/Coordination/<today>-identity-mapping.md` directly to update; the skill picks up changes on next invocation.

If `~/Documents/Coordination/` is missing or empty, the skill falls back to the vault mirror at `=notes/inbox/agent-coordination.md`.

## Roadmap

- **v0.1** (shipped 2026-04-20) — `fleet-identity` skill.
- **v0.2** (this release, 2026-04-24) — Hermes MCP messaging bridge + `hermes-bridge` skill. Plan: `=notes/docs/plans/2026-04-24-autonomous-ai-agent-Hermes-MCP-impl.md`.
- **v0.3** (planned) — Zolivier/Zoe MCP wiring via OpenClaw, analogous to the Hermes side.

## Related

- Sibling skill `hermes-cli` (in `=notes/.claude/skills/hermes-cli/`) — TTY one-shot delegation via `hermes chat -Q -q`. Complementary to `hermes-bridge`.
- `dizzy.py` IDENTITIES (in `=notes/claude/scripts/`) — Discord routing primitive (tokens, channels). Different concern from semantic identity.
- Hermes Agent: <https://hermes-agent.nousresearch.com/>

## License

MIT — see LICENSE.
