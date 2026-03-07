# PI Pathfinder

Routes your task to the best installed plugin automatically.

[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen)](.)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## How It Works

1. **Builds a JSON index** of every plugin installed in your Claude Code cache
   (`~/.claude/plugins/cache/`), extracting names, descriptions, keywords, and
   skill paths.
2. **Matches your intent** against that index using keyword and description
   scoring.
3. **Invokes the best match** via the `Skill` tool, so the matched plugin's
   skill runs directly.

You describe what you want in plain language. PI Pathfinder finds the right
plugin and hands off to it.

---

## Usage

Just describe your task:

```
"format my code"
"scan for secrets"
"generate smart commits"
```

PI Pathfinder searches your installed plugins, picks the best match, and
invokes its skill. No need to remember plugin names or commands.

---

## Rebuilding the Index

The plugin index is built automatically when needed. To rebuild it manually:

```bash
python3 scripts/build_index.py [--cache-dir PATH] [--output PATH]
```

- `--cache-dir` defaults to `~/.claude/plugins/cache/`
- `--output` defaults to `plugin_index.json` in the PI Pathfinder directory

---

## What Gets Indexed

For each plugin in your cache, the indexer reads:

- `plugin.json` (name, description, keywords)
- `skills/*/SKILL.md` (skill definitions and instructions)

The resulting `plugin_index.json` is a flat list of entries with fields for
name, description, keywords, and skill paths -- everything needed for fast
matching.

---

## Limitations

- Searches only plugins you have installed -- not the full marketplace.
- Match quality depends on how well plugins define their keywords and
  descriptions.
- Cannot execute MCP server code directly; it invokes skills via the Skill
  tool.

---

## Version

2.0.0

## License

MIT
