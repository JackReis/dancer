#!/usr/bin/env python3
"""
pi-pathfinder index builder.
Scans ~/.claude/plugins/cache/ and builds a searchable JSON index
of all installed plugins, their skills, commands, agents, and hooks.
"""
import json
import re
from pathlib import Path
from typing import Dict, Optional, List


def parse_frontmatter(content: str) -> Dict[str, str]:
    """Extract name and description from YAML frontmatter.

    Handles:
    - Standard single-line values: name: value
    - Multiline values: description: |\\n  line1\\n  line2
    - Missing frontmatter (returns {})
    """
    if not content.startswith("---"):
        return {}

    # Find the closing ---
    second_fence = content.find("---", 3)
    if second_fence == -1:
        return {}

    fm_block = content[3:second_fence].strip()
    result = {}

    lines = fm_block.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Match key: value pairs
        match = re.match(r'^(\w[\w-]*)\s*:\s*(.*)', line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()

            # Check for multiline indicator |
            if value == "|":
                # Collect indented continuation lines
                multiline_parts = []
                i += 1
                while i < len(lines) and (lines[i].startswith("  ") or lines[i].strip() == ""):
                    multiline_parts.append(lines[i].strip())
                    i += 1
                value = " ".join(part for part in multiline_parts if part)
                if key in ("name", "description"):
                    result[key] = value
                continue

            if key in ("name", "description"):
                result[key] = value

        i += 1

    return result


def scan_plugin(plugin_version_dir: Path, marketplace: str) -> Optional[Dict]:
    """Scan a single plugin directory and extract metadata.

    Args:
        plugin_version_dir: Path like cache/<marketplace>/<plugin>/<version>/
        marketplace: Name of the marketplace this plugin belongs to

    Returns:
        Dict with plugin metadata, or None if invalid plugin.
    """
    plugin_json_path = plugin_version_dir / ".claude-plugin" / "plugin.json"
    if not plugin_json_path.exists():
        return None

    try:
        with open(plugin_json_path) as f:
            pj = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    plugin_name = pj.get("name", plugin_version_dir.parent.name)

    # Scan skills
    skills = []
    skills_dir = plugin_version_dir / "skills"
    if skills_dir.exists():
        for skill_dir in sorted(skills_dir.iterdir()):
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                fm = parse_frontmatter(skill_md.read_text())
                skill_name = fm.get("name", skill_dir.name)
                skills.append({
                    "name": skill_name,
                    "description": fm.get("description", ""),
                    "skill_path": f"{plugin_name}:{skill_name}",
                })

    # Scan commands
    commands = []
    commands_dir = plugin_version_dir / "commands"
    if commands_dir.exists():
        for cmd_file in sorted(commands_dir.glob("*.md")):
            fm = parse_frontmatter(cmd_file.read_text())
            commands.append({
                "name": fm.get("name", cmd_file.stem),
                "description": fm.get("description", ""),
            })

    # Scan agents
    agents = []
    agents_dir = plugin_version_dir / "agents"
    if agents_dir.exists():
        for agent_file in sorted(agents_dir.glob("*.md")):
            fm = parse_frontmatter(agent_file.read_text())
            agents.append({
                "name": fm.get("name", agent_file.stem),
                "description": fm.get("description", ""),
            })

    return {
        "name": plugin_name,
        "marketplace": marketplace,
        "version": pj.get("version", "unknown"),
        "description": pj.get("description", ""),
        "keywords": pj.get("keywords", []),
        "skills": skills,
        "commands": commands,
        "agents": agents,
    }
