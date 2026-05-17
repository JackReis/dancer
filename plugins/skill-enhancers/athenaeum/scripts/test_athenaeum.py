#!/usr/bin/env python3
"""Comprehensive unit tests for the athenaeum bootstrap CLI script."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.resolve() / "athenaeum"


class AthenaeumTests(unittest.TestCase):
    """Tests covering init, diff, sign, and check subcommands."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.orig_dir = os.getcwd()
        os.chdir(self.tmpdir.name)
        self.env = os.environ.copy()
        self.env["KIMI_CLI"] = "1"

    def tearDown(self):
        os.chdir(self.orig_dir)
        self.tmpdir.cleanup()

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=self.env,
            cwd=self.tmpdir.name,
        )

    # ------------------------------------------------------------------
    # Step 1: init --mode design
    # ------------------------------------------------------------------
    def test_init_design(self):
        result = self._run("init", "test-topic", "--mode", "design")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        design_md = Path(self.tmpdir.name) / ".athenaeum" / "test-topic" / "DESIGN.md"
        self.assertTrue(design_md.exists(), "DESIGN.md should exist")
        content = design_md.read_text()
        self.assertIn("test-topic", content, "DESIGN.md should contain topic name")

    def test_init_design_no_a2a_by_default(self):
        """Default transport is filesystem — no task.json should be created."""
        result = self._run("init", "test-topic", "--mode", "design")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"
        task_files = list(topic_dir.glob("*/task.json"))
        self.assertEqual(len(task_files), 0, "task.json should NOT exist with default transport")

    def test_init_design_creates_task_json_when_a2a(self):
        result = self._run("init", "test-topic", "--mode", "design", "--transport", "a2a")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"
        task_files = list(topic_dir.glob("*/task.json"))
        self.assertTrue(len(task_files) > 0, "task.json should exist under a task-id directory")
        data = json.loads(task_files[0].read_text())
        self.assertEqual(data["metadata"]["athenaeum_mode"], "design")
        self.assertEqual(data["status"], "submitted")

    # ------------------------------------------------------------------
    # Step 2: init --mode reconcile
    # ------------------------------------------------------------------
    def test_init_reconcile(self):
        result = self._run("init", "test-topic", "--mode", "reconcile")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"

        claims_tmpl = topic_dir / "claims.yaml.template"
        grill_log = topic_dir / "grill-log.md"
        diff_md = topic_dir / "diff.md"

        self.assertTrue(claims_tmpl.exists(), "claims.yaml.template should exist")
        self.assertTrue(grill_log.exists(), "grill-log.md should exist")
        self.assertTrue(diff_md.exists(), "diff.md should exist")

        tmpl_text = claims_tmpl.read_text()
        self.assertIn("agent:", tmpl_text, "Template should contain 'agent:'")
        self.assertIn("claims:", tmpl_text, "Template should contain 'claims:'")
        self.assertIn("scope:", tmpl_text, "Template should contain 'scope:'")

    # ------------------------------------------------------------------
    # Step 3: init --mode ratify
    # ------------------------------------------------------------------
    def test_init_ratify(self):
        result = self._run(
            "init", "test-topic", "--mode", "ratify", "--roster", "kimi-cli,agent-b"
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"

        manifest = topic_dir / "manifest.yaml"
        artifact = topic_dir / "artifact.md"
        log_md = topic_dir / "log.md"

        self.assertTrue(manifest.exists(), "manifest.yaml should exist")
        self.assertTrue(artifact.exists(), "artifact.md should exist")
        self.assertTrue(log_md.exists(), "log.md should exist")

        manifest_text = manifest.read_text()
        self.assertIn("topic: test-topic", manifest_text)
        self.assertIn("initiator: kimi-cli", manifest_text)
        self.assertIn("status: open", manifest_text)
        self.assertIn("mode: standard", manifest_text)
        self.assertIn("expires_at:", manifest_text)
        self.assertIn("roster:", manifest_text)
        self.assertIn("kimi-cli", manifest_text)
        self.assertIn("agent-b", manifest_text)

        # Vote files should NOT be auto-created (agents write them)
        self.assertFalse(
            (topic_dir / "kimi-cli.vote.yaml").exists(),
            "Vote files should not be created during init",
        )
        self.assertFalse(
            (topic_dir / "agent-b.vote.yaml").exists(),
            "Vote files should not be created during init",
        )

    def test_init_ratify_default_roster(self):
        """When no --roster is provided, default to the current agent."""
        result = self._run("init", "test-topic", "--mode", "ratify")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"
        manifest_text = (topic_dir / "manifest.yaml").read_text()
        self.assertIn("kimi-cli", manifest_text, "Default roster should include current agent")

    def test_init_ratify_fast_mode(self):
        result = self._run("init", "test-topic", "--mode", "ratify", "--ratify-mode", "fast")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"
        manifest_text = (topic_dir / "manifest.yaml").read_text()
        self.assertIn("mode: fast", manifest_text)

    # ------------------------------------------------------------------
    # Step 4: diff
    # ------------------------------------------------------------------
    def test_diff_three_buckets(self):
        self._run("init", "test-topic", "--mode", "reconcile")
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"

        # Agent A knows claim-1, claim-2
        (topic_dir / "agent-a.claims.yaml").write_text(
            "agent: agent-a\n"
            "claims:\n"
            "  - id: claim-1\n"
            "    statement: Both know this\n"
            "  - id: claim-2\n"
            "    statement: Only A knows this\n"
        )

        # Agent B knows claim-1, claim-3
        (topic_dir / "agent-b.claims.yaml").write_text(
            "agent: agent-b\n"
            "claims:\n"
            "  - id: claim-1\n"
            "    statement: Both know this\n"
            "  - id: claim-3\n"
            "    statement: B and C know this\n"
        )

        # Agent C knows claim-1, claim-3
        (topic_dir / "agent-c.claims.yaml").write_text(
            "agent: agent-c\n"
            "claims:\n"
            "  - id: claim-1\n"
            "    statement: Both know this\n"
            "  - id: claim-3\n"
            "    statement: B and C know this\n"
        )

        result = self._run("diff", "test-topic")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout

        self.assertIn("agreed", output, "Should contain agreed bucket")
        self.assertIn("disagreed", output, "Should contain disagreed bucket")
        self.assertIn("only-one-knows", output, "Should contain only-one-knows bucket")
        self.assertIn("claim-1", output)
        self.assertIn("claim-2", output)
        self.assertIn("claim-3", output)

    def test_diff_insufficient_claims(self):
        self._run("init", "test-topic", "--mode", "reconcile")
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"
        (topic_dir / "agent-a.claims.yaml").write_text(
            "agent: agent-a\nclaims:\n  - id: claim-1\n"
        )
        result = self._run("diff", "test-topic")
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("Need at least 2 claims files", result.stdout + result.stderr)

    # ------------------------------------------------------------------
    # Step 5: sign
    # ------------------------------------------------------------------
    def test_sign_creates_signoff(self):
        self._run("init", "test-topic", "--mode", "reconcile")
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"
        merged = topic_dir / "state.merged.yaml"
        merged.write_text("key: value\nnested:\n  item: 1\n")

        result = self._run("sign", "test-topic")
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        signoff = topic_dir / "signoff.md"
        self.assertTrue(signoff.exists(), "signoff.md should exist")
        text = signoff.read_text()
        self.assertIn("agent: kimi-cli", text)
        self.assertIn("merged_state_sha256:", text)
        self.assertIn("timestamp:", text)
        self.assertIn("attestation:", text)

        # Verify SHA-256 matches the file content
        content = merged.read_text().replace("\r\n", "\n").replace("\r", "\n")
        expected_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        self.assertIn(expected_sha, text, "SHA-256 should match file content")

    def test_sign_appends(self):
        self._run("init", "test-topic", "--mode", "reconcile")
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"
        merged = topic_dir / "state.merged.yaml"
        merged.write_text("version: 1\n")

        self._run("sign", "test-topic")
        self._run("sign", "test-topic")

        signoff = topic_dir / "signoff.md"
        text = signoff.read_text()
        # Two signoffs should produce two agent lines
        self.assertEqual(text.count("agent: kimi-cli"), 2, "Should append each signoff")

    def test_sign_missing_merged(self):
        self._run("init", "test-topic", "--mode", "reconcile")
        result = self._run("sign", "test-topic")
        self.assertEqual(result.returncode, 1, msg=result.stdout)
        self.assertIn("No state.merged.yaml found", result.stdout + result.stderr)

    # ------------------------------------------------------------------
    # Step 6: check
    # ------------------------------------------------------------------
    def test_check_detects_awaiting_and_resolved(self):
        # Scaffold a ratify topic with current agent in roster
        result = self._run(
            "init", "test-topic", "--mode", "ratify", "--roster", "kimi-cli"
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"

        # check should detect open ratification awaiting this agent
        result = self._run("check")
        self.assertEqual(result.returncode, 0)
        self.assertIn("AWAITING VOTE: test-topic", result.stdout)

        # Agent writes their vote file
        (topic_dir / "kimi-cli.vote.yaml").write_text(
            "agent: kimi-cli\n"
            "artifact_sha256: abc123def456\n"
            "decision: SIGN\n"
            "timestamp: 2026-01-01T00:00:00Z\n"
        )

        # check should no longer report it as awaiting
        result = self._run("check")
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("AWAITING VOTE: test-topic", result.stdout)
        self.assertIn(
            "No open ratifications awaiting your vote.", result.stdout
        )

    def test_check_not_in_roster(self):
        """If current agent is not in roster, check should not report it."""
        self._run("init", "test-topic", "--mode", "ratify", "--roster", "other-agent")
        result = self._run("check")
        self.assertEqual(result.returncode, 0)
        self.assertIn("No open ratifications awaiting your vote.", result.stdout)

    def test_check_closed_status(self):
        """If status is not open/pending-human, check should ignore it."""
        self._run("init", "test-topic", "--mode", "ratify", "--roster", "kimi-cli")
        topic_dir = Path(self.tmpdir.name) / ".athenaeum" / "test-topic"
        manifest = topic_dir / "manifest.yaml"
        # Change status to ratified
        content = manifest.read_text().replace("status: open", "status: ratified")
        manifest.write_text(content)

        result = self._run("check")
        self.assertEqual(result.returncode, 0)
        self.assertIn("No open ratifications awaiting your vote.", result.stdout)

    def test_check_no_athenaeum_dir(self):
        result = self._run("check")
        self.assertEqual(result.returncode, 0)
        self.assertIn("No .athenaeum/ directory found.", result.stdout)

    def test_detect_agent_slug_from_card(self):
        """Verify that _detect_agent_slug picks up identity from .well-known/agent.json."""
        well_known = Path(self.tmpdir.name) / ".well-known"
        well_known.mkdir()
        (well_known / "agent.json").write_text(json.dumps({"name": "card-agent-slug"}))
        
        # We need to run init to see the initiator name in manifest.yaml
        result = self._run("init", "card-topic", "--mode", "ratify")
        self.assertEqual(result.returncode, 0)
        
        manifest = Path(self.tmpdir.name) / ".athenaeum" / "card-topic" / "manifest.yaml"
        self.assertIn("initiator: card-agent-slug", manifest.read_text())

    def test_poll_topic(self):
        self._run("init", "test-topic", "--mode", "design", "--transport", "a2a")
        result = self._run("poll", "test-topic")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("status=submitted", result.stdout)

    def test_poll_missing_topic(self):
        result = self._run("poll", "nonexistent-topic")
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
