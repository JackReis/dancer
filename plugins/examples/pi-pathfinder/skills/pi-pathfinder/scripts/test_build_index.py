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
from build_index import parse_frontmatter, scan_plugin, build_index


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


class TestBuildIndex(unittest.TestCase):
    """Test building the full plugin index."""

    def setUp(self):
        """Create a fake cache directory with 2 marketplaces, 3 plugins."""
        self.tmpdir = tempfile.mkdtemp()
        self.cache_dir = Path(self.tmpdir) / "cache"

        # Marketplace 1: two plugins
        for name, desc, kw in [
            ("formatter", "Format code with Prettier", ["format", "prettier"]),
            ("secret-scanner", "Scan for exposed secrets", ["security", "secrets"]),
        ]:
            pdir = self.cache_dir / "marketplace-a" / name / "1.0.0"
            (pdir / ".claude-plugin").mkdir(parents=True)
            (pdir / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"name": name, "description": desc, "keywords": kw, "version": "1.0.0"})
            )
            (pdir / "skills" / name).mkdir(parents=True)
            (pdir / "skills" / name / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: {desc}\n---\n"
            )

        # Marketplace 2: one plugin that should be self-excluded
        pdir = self.cache_dir / "marketplace-b" / "pi-pathfinder" / "1.0.0"
        (pdir / ".claude-plugin").mkdir(parents=True)
        (pdir / ".claude-plugin" / "plugin.json").write_text(
            '{"name": "pi-pathfinder", "description": "Plugin router", "version": "1.0.0"}'
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_build_index_finds_all_plugins(self):
        index = build_index(self.cache_dir)
        self.assertEqual(index["plugin_count"], 2)  # pi-pathfinder excluded
        names = [p["name"] for p in index["plugins"]]
        self.assertIn("formatter", names)
        self.assertIn("secret-scanner", names)
        self.assertNotIn("pi-pathfinder", names)

    def test_build_index_has_metadata(self):
        index = build_index(self.cache_dir)
        self.assertIn("built_at", index)
        self.assertIn("plugin_count", index)
        self.assertIn("skill_count", index)
        self.assertEqual(index["skill_count"], 2)

    def test_build_index_empty_cache(self):
        empty = Path(self.tmpdir) / "empty-cache"
        empty.mkdir()
        index = build_index(empty)
        self.assertEqual(index["plugin_count"], 0)
        self.assertEqual(index["plugins"], [])


if __name__ == "__main__":
    unittest.main()
