import os
import shutil
import tempfile
import unittest
import pathlib
import subprocess
import sys

# Add the scripts dir to path so we can import if we want, 
# but we'll mostly test via subprocess to simulate CLI.
SCRIPTS_DIR = pathlib.Path(__file__).parent.parent / "scripts"
SCRIPT_PATH = SCRIPTS_DIR / "fleet_ratify.py"

class TestFleetRatify(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.vault_root = pathlib.Path(self.test_dir) / "vault"
        self.vault_root.mkdir()
        self.ratify_dir = self.vault_root / ".fleet-ratify"
        
        # Patch the script to use our temp vault
        with open(SCRIPT_PATH, "r") as f:
            self.script_content = f.read()
        
        self.patched_script = pathlib.Path(self.test_dir) / "fleet_ratify_patched.py"
        patched_content = self.script_content.replace(
            'VAULT_ROOT = pathlib.Path("/Users/jack.reis/Documents/=notes")',
            f'VAULT_ROOT = pathlib.Path("{self.vault_root}")'
        )
        self.patched_script.write_text(patched_content)
        self.patched_script.chmod(0o755)
        
        # Create a dummy artifact
        self.artifact = pathlib.Path(self.test_dir) / "test_artifact.md"
        self.artifact.write_text("# Test Artifact\nThis is a test.")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def run_cmd(self, args, agent_id="pt"):
        env = os.environ.copy()
        env["AGENT_ID"] = agent_id
        result = subprocess.run(
            [sys.executable, str(self.patched_script)] + args,
            capture_output=True,
            text=True,
            env=env
        )
        return result

    def test_full_flow_unanimous(self):
        # 1. Init
        res = self.run_cmd(["init", str(self.artifact), "--roster", "agent-a,agent-b", "--topic", "test-topic"])
        self.assertEqual(res.returncode, 0)
        self.assertTrue((self.ratify_dir / "test-topic" / "manifest.yaml").exists())
        
        # 2. Vote agent-a
        res = self.run_cmd(["vote", "test-topic", "sign"], agent_id="agent-a")
        self.assertEqual(res.returncode, 0)
        self.assertTrue((self.ratify_dir / "test-topic" / "agent-a.vote.yaml").exists())
        
        # 3. Vote agent-b
        res = self.run_cmd(["vote", "test-topic", "sign"], agent_id="agent-b")
        self.assertEqual(res.returncode, 0)
        self.assertTrue((self.ratify_dir / "test-topic" / "agent-b.vote.yaml").exists())
        
        # 4. Tally (agent-a is merge writer as it sorts first)
        res = self.run_cmd(["tally", "test-topic"], agent_id="agent-a")
        self.assertEqual(res.returncode, 0)
        self.assertIn("RATIFIED", res.stdout)
        self.assertTrue((self.ratify_dir / "test-topic" / "ratified.md").exists())
        
        # Verify status in manifest
        manifest = (self.ratify_dir / "test-topic" / "manifest.yaml").read_text()
        self.assertIn("status: ratified", manifest)

    def test_dissent_flow(self):
        # 1. Init
        self.run_cmd(["init", str(self.artifact), "--roster", "agent-a,agent-b", "--topic", "test-dissent"])
        
        # 2. Vote agent-a (sign)
        self.run_cmd(["vote", "test-dissent", "sign"], agent_id="agent-a")
        
        # 3. Vote agent-b (dissent)
        self.run_cmd(["vote", "test-dissent", "dissent", "--reason", "Bad wording"], agent_id="agent-b")
        
        # 4. Tally (agent-a is merge writer)
        res = self.run_cmd(["tally", "test-dissent"], agent_id="agent-a")
        self.assertEqual(res.returncode, 0)
        self.assertIn("DECOMPOSED", res.stdout)
        self.assertTrue((self.ratify_dir / "test-dissent" / "decomposition.md").exists())
        self.assertTrue((self.ratify_dir / "test-dissent" / "human-decision.yaml").exists())
        
        # Verify status in manifest
        manifest = (self.ratify_dir / "test-dissent" / "manifest.yaml").read_text()
        self.assertIn("status: pending-human", manifest)

if __name__ == "__main__":
    unittest.main()
