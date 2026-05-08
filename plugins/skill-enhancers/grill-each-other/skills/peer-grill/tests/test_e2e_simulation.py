"""tests/test_e2e_simulation.py — end-to-end peer-grill protocol simulation.

The plugin-dev harness can't reliably spawn 2 live Claude sessions, so we
simulate the peer ('agent-b') by pre-staging its files at each protocol
step. The local agent ('agent-a') uses the actual protocol scripts.

This proves the file conventions and scripts produce a valid converged state
when both sides follow the protocol — which is the only correctness claim
the skill makes (the protocol can't compel a peer to actually show up).
"""
import subprocess
import pathlib
import tempfile
import sys
import shutil
import hashlib
import os

SKILL = pathlib.Path.home() / ".claude/skills/peer-grill"
SCRIPTS = SKILL / "scripts"

CANDIDATE_PYTHONS = [
    sys.executable,
    "/usr/bin/python3",
    "/opt/homebrew/bin/python3",
    str(pathlib.Path.home() / ".mcp-venv/bin/python3"),
]


def python_with_yaml():
    for py in CANDIDATE_PYTHONS:
        try:
            r = subprocess.run([py, "-c", "import yaml"], capture_output=True)
            if r.returncode == 0:
                return py
        except (FileNotFoundError, OSError):
            continue
    return None


def sh(*args, cwd=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, (
        f"FAILED: {' '.join(str(a) for a in args)}\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    return r.stdout


def test_full_protocol_converges():
    py_yaml = python_with_yaml()
    if py_yaml is None:
        print("SKIP: PyYAML not found; install via `pip install pyyaml`")
        return
    workspace = pathlib.Path(tempfile.mkdtemp())
    os.chdir(workspace)

    # Step 1: agent-a bootstraps (use a long unique slug to avoid colliding
    # with any real reconciliation state)
    topic_slug = "test-fixture-2026-05-03-shipping"
    sh("bash", str(SCRIPTS / "peer_grill_init.sh"), topic_slug, "agent-a")
    topic = workspace / ".peer-grill" / topic_slug
    assert topic.is_dir()

    # Step 2: agent-a fills in real claims (overwrite skeleton)
    (topic / "agent-a.claims.yaml").write_text(
        """agent: agent-a
session_started: 2026-05-03T00:00:00Z
scope: [infra]
claims:
  - id: db-version
    statement: postgres 15.4 in production
    confidence: high
    source: kubectl get pods -n prod
    scope: infra
    last_verified: 2026-05-03T00:00:00Z
"""
    )

    # Step 3: SIMULATED PEER — pre-stage agent-b's claims.yaml
    (topic / "agent-b.claims.yaml").write_text(
        """agent: agent-b
session_started: 2026-05-03T00:00:00Z
scope: [infra]
claims:
  - id: db-version
    statement: postgres 15.4 in production
    confidence: high
    source: helm values.yaml
    scope: infra
    last_verified: 2026-05-03T00:00:00Z
"""
    )

    # Step 4: agent-a runs diff (needs PyYAML, so use the detected python)
    sh(py_yaml, str(SCRIPTS / "peer_grill_diff.py"), str(topic))
    diff = (topic / "diff.md").read_text()
    assert "AGREED" in diff and "db-version" in diff, diff

    # Step 5: both agents write RATIFY lines (agent-b's is simulated).
    # Use the inline-arrow format so we exercise both paths in the suite.
    log = topic / "grill-log.md"
    log.write_text(
        "[2026-05-03T00:05:00Z] agent-a -> agent-b | claim:db-version | round:1\n"
        "Q: Does your source agree it is 15.4 specifically?\n"
        "[2026-05-03T00:05:30Z] agent-b -> agent-a | claim:db-version | round:1\n"
        "A: helm values.yaml line 42 sets image tag postgres:15.4-bookworm\n"
        "[2026-05-03T00:06:00Z] agent-a -> agent-b | claim:db-version | RATIFY: db-version | postgres 15.4 in production\n"
        "[2026-05-03T00:06:10Z] agent-b -> agent-a | claim:db-version | RATIFY: db-version | postgres 15.4 in production\n"
    )

    # Step 6: convergence check
    sh(
        sys.executable,
        str(SCRIPTS / "peer_grill_check_convergence.py"),
        str(topic),
        "db-version",
    )

    # Step 7: write merged state
    merged_text = """topic: test-fixture-2026-05-03-shipping
ratified_at: 2026-05-03T00:07:00Z
peers: [agent-a, agent-b]
claims:
  - id: db-version
    statement: postgres 15.4 in production
    sources: [kubectl get pods -n prod, helm values.yaml]
    scope: infra
"""
    (topic / "state.merged.yaml").write_text(merged_text)
    expected_sha = hashlib.sha256(merged_text.encode()).hexdigest()

    # Step 8: both signoffs
    sh(sys.executable, str(SCRIPTS / "peer_grill_signoff.py"), str(topic), "agent-a")
    sh(sys.executable, str(SCRIPTS / "peer_grill_signoff.py"), str(topic), "agent-b")

    # Step 9: verify both signoff sha256 values match
    signoff = (topic / "signoff.md").read_text()
    assert signoff.count(expected_sha) == 2, (
        f"expected 2 matching sha256 in signoff.md, got:\n{signoff}"
    )
    assert "agent-a" in signoff and "agent-b" in signoff

    shutil.rmtree(workspace)


if __name__ == "__main__":
    test_full_protocol_converges()
    print("PASS - full peer-grill protocol simulation converged")
