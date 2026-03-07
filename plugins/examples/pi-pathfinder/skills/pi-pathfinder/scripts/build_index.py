#!/usr/bin/env python3
"""
pi-pathfinder index builder.
Scans ~/.claude/plugins/cache/ and builds a searchable JSON index
of all installed plugins, their skills, commands, agents, and hooks.
"""
import re
from pathlib import Path
from typing import Dict


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
