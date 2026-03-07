#!/usr/bin/env python3
"""Tests for pi-pathfinder build_index.py"""
import unittest
import tempfile
import json
import os
from pathlib import Path

# Import from same directory
import sys
sys.path.insert(0, os.path.dirname(__file__))
from build_index import parse_frontmatter


class TestParseFrontmatter(unittest.TestCase):
    """Test YAML frontmatter extraction from SKILL.md files."""

    def test_standard_frontmatter(self):
        content = """---
name: format-check
description: Check if files are properly formatted without making changes
allowed-tools: Read, Bash
version: 1.0.0
---

# Format Check Skill
"""
        result = parse_frontmatter(content)
        self.assertEqual(result["name"], "format-check")
        self.assertEqual(result["description"], "Check if files are properly formatted without making changes")

    def test_multiline_description(self):
        content = """---
name: my-skill
description: |
  This is a multiline
  description field
version: 1.0.0
---

# Content
"""
        result = parse_frontmatter(content)
        self.assertEqual(result["name"], "my-skill")
        self.assertIn("multiline", result["description"])

    def test_no_frontmatter(self):
        content = "# Just a heading\nSome content"
        result = parse_frontmatter(content)
        self.assertEqual(result, {})

    def test_missing_name(self):
        content = """---
description: Has description but no name
---
"""
        result = parse_frontmatter(content)
        self.assertEqual(result.get("name"), None)
        self.assertEqual(result["description"], "Has description but no name")


if __name__ == "__main__":
    unittest.main()
