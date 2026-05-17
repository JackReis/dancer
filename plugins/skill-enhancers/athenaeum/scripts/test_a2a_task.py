import json, os, sys, tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))


def test_task_roundtrip():
    from a2a_task import Task, TaskStatus, save_task, load_task
    t = Task(
        id="test-001",
        session_id="sess-001",
        status=TaskStatus.SUBMITTED,
        metadata={"athenaeum_mode": "reconcile", "round_budget": 3},
    )
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        save_task(t, d)
        t2 = load_task(d / "test-001" / "task.json")
        assert t2.id == "test-001"
        assert t2.status == TaskStatus.SUBMITTED
        assert t2.metadata["athenaeum_mode"] == "reconcile"


def test_artifact_roundtrip():
    from a2a_task import Artifact
    a = Artifact(
        name="claims",
        mime_type="application/yaml",
        parts=[{"type": "text", "text": "agent: test"}],
        metadata={"topic": "pricing"},
    )
    d = a.to_dict()
    a2 = Artifact.from_dict(d)
    assert a2.name == "claims"
    assert a2.mime_type == "application/yaml"
    assert a2.parts[0]["text"] == "agent: test"


def test_init_task():
    from a2a_task import init_task, TaskStatus
    t = init_task("pricing", "reconcile")
    assert t.id.startswith("athenaeum-reconcile-pricing-")
    assert t.status == TaskStatus.SUBMITTED
    assert t.metadata["athenaeum_mode"] == "reconcile"


if __name__ == "__main__":
    test_task_roundtrip()
    test_artifact_roundtrip()
    test_init_task()
    print("[test_a2a_task] PASS")
