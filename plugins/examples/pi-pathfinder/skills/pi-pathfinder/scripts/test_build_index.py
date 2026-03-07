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
from build_index import parse_frontmatter, scan_plugin


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


class TestScanPlugin(unittest.TestCase):
    """Test scanning a single plugin directory."""

    def setUp(self):
        """Create a fake plugin directory structure."""
        self.tmpdir = tempfile.mkdtemp()
        self.plugin_dir = Path(self.tmpdir) / "test-plugin" / "1.0.0"

        # Create plugin.json
        pj_dir = self.plugin_dir / ".claude-plugin"
        pj_dir.mkdir(parents=True)
        (pj_dir / "plugin.json").write_text(
            '{"name": "test-plugin", "description": "A test plugin", '
            '"keywords": ["test", "example"], "version": "1.0.0"}'
        )

        # Create a skill
        skill_dir = self.plugin_dir / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: my-skill\ndescription: Does testing things\n---\n# My Skill"
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_scan_plugin_basic(self):
        result = scan_plugin(self.plugin_dir, "test-marketplace")
        self.assertEqual(result["name"], "test-plugin")
        self.assertEqual(result["marketplace"], "test-marketplace")
        self.assertEqual(result["description"], "A test plugin")
        self.assertEqual(result["keywords"], ["test", "example"])
        self.assertEqual(len(result["skills"]), 1)
        self.assertEqual(result["skills"][0]["name"], "my-skill")
        self.assertEqual(result["skills"][0]["skill_path"], "test-plugin:my-skill")

    def test_scan_plugin_no_plugin_json(self):
        empty = Path(self.tmpdir) / "empty" / "1.0.0"
        empty.mkdir(parents=True)
        result = scan_plugin(empty, "test-marketplace")
        self.assertIsNone(result)

    def test_scan_plugin_no_skills(self):
        no_skills = Path(self.tmpdir) / "no-skills" / "1.0.0"
        pj_dir = no_skills / ".claude-plugin"
        pj_dir.mkdir(parents=True)
        (pj_dir / "plugin.json").write_text(
            '{"name": "no-skills", "description": "Plugin without skills", "version": "1.0.0"}'
        )
        result = scan_plugin(no_skills, "test-marketplace")
        self.assertEqual(result["name"], "no-skills")
        self.assertEqual(result["skills"], [])


if __name__ == "__main__":
    unittest.main()
