import json, os, sys, tempfile, threading, time, urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))


def test_tasks_send():
    from a2a_rpc import A2ARPCServer, A2AHandler
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["ATHENAEUM_VAULT"] = tmp
        server = A2ARPCServer(("127.0.0.1", 18765), A2AHandler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        time.sleep(0.2)

        try:
            req = urllib.request.Request(
                "http://127.0.0.1:18765/",
                data=json.dumps({
                    "jsonrpc": "2.0",
                    "method": "tasks/send",
                    "params": {"task": {"id": "t1", "sessionId": "s1", "status": "submitted"}},
                    "id": 1,
                }).encode(),
                headers={"Content-Type": "application/json"},
            )
            resp = urllib.request.urlopen(req)
            data = json.loads(resp.read())
            assert data["jsonrpc"] == "2.0"
            assert data["result"]["task"]["id"] == "t1"
            assert data["result"]["task"]["status"] == "submitted"
        finally:
            server.shutdown()
            del os.environ["ATHENAEUM_VAULT"]


def test_tasks_get():
    from a2a_rpc import A2ARPCServer, A2AHandler
    from a2a_task import Task, TaskStatus, save_task
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["ATHENAEUM_VAULT"] = tmp
        server = A2ARPCServer(("127.0.0.1", 18766), A2AHandler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        time.sleep(0.2)
        try:
            # First send a task
            req = urllib.request.Request(
                "http://127.0.0.1:18766/",
                data=json.dumps({
                    "jsonrpc": "2.0",
                    "method": "tasks/send",
                    "params": {"task": {"id": "t2", "sessionId": "s2", "status": "submitted", "metadata": {"topic": "test"}}},
                    "id": 1,
                }).encode(),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req)

            # Then get it
            req = urllib.request.Request(
                "http://127.0.0.1:18766/",
                data=json.dumps({
                    "jsonrpc": "2.0",
                    "method": "tasks/get",
                    "params": {"id": "t2", "topic": "test"},
                    "id": 2,
                }).encode(),
                headers={"Content-Type": "application/json"},
            )
            resp = urllib.request.urlopen(req)
            data = json.loads(resp.read())
            assert data["result"]["task"]["id"] == "t2"
        finally:
            server.shutdown()
            del os.environ["ATHENAEUM_VAULT"]


def test_tasks_cancel():
    from a2a_rpc import A2ARPCServer, A2AHandler
    import urllib.request
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["ATHENAEUM_VAULT"] = tmp
        server = A2ARPCServer(("127.0.0.1", 18767), A2AHandler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        time.sleep(0.2)
        try:
            # Send
            urllib.request.urlopen(urllib.request.Request(
                "http://127.0.0.1:18767/",
                data=json.dumps({
                    "jsonrpc": "2.0", "method": "tasks/send",
                    "params": {"task": {"id": "t3", "sessionId": "s3", "status": "submitted", "metadata": {"topic": "test"}}},
                    "id": 1,
                }).encode(), headers={"Content-Type": "application/json"}))
            # Cancel
            req = urllib.request.Request(
                "http://127.0.0.1:18767/",
                data=json.dumps({
                    "jsonrpc": "2.0", "method": "tasks/cancel",
                    "params": {"id": "t3", "topic": "test"},
                    "id": 2,
                }).encode(), headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req)
            data = json.loads(resp.read())
            assert data["result"]["task"]["status"] == "canceled"
        finally:
            server.shutdown()
            del os.environ["ATHENAEUM_VAULT"]


def test_tasks_send_subscribe():
    from a2a_rpc import A2ARPCServer, A2AHandler
    from a2a_task import Task, TaskStatus, save_task
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["ATHENAEUM_VAULT"] = tmp
        server = A2ARPCServer(("127.0.0.1", 18768), A2AHandler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        time.sleep(0.2)
        try:
            # Seed a task first
            task = Task(id="t4", session_id="s4", status=TaskStatus.SUBMITTED,
                        metadata={"topic": "test"})
            save_task(task, Path(tmp) / ".athenaeum" / "test")

            req = urllib.request.Request(
                "http://127.0.0.1:18768/",
                data=json.dumps({
                    "jsonrpc": "2.0", "method": "tasks/sendSubscribe",
                    "params": {"id": "t4", "topic": "test"},
                    "id": 4,
                }).encode(), headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req, timeout=2)
            # Read first SSE line
            line = resp.readline().decode()
            assert line.startswith("data:")
            data = json.loads(line[5:].strip())
            assert data["id"] == "t4"
            assert data["status"] == "submitted"
        finally:
            server.shutdown()
            del os.environ["ATHENAEUM_VAULT"]


if __name__ == "__main__":
    test_tasks_send()
    test_tasks_get()
    test_tasks_cancel()
    test_tasks_send_subscribe()
    print("[test_a2a_rpc] PASS")
