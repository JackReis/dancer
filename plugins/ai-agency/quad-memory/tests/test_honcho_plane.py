from unittest.mock import MagicMock, patch

from quad_memory.core import PlaneResult, TurnMemory


def _fake_client():
    client = MagicMock()
    human = MagicMock()
    assistant = MagicMock()
    session = MagicMock()
    client.peer.side_effect = lambda pid: assistant if pid == "claude-code" else human
    client.session.return_value = session
    assistant.chat.return_value = "Jack prefers local-first, secrets via SOPS."
    return client, human, assistant, session


def test_capture_writes_both_peers():
    from quad_memory import honcho_plane as hp
    client, human, assistant, session = _fake_client()
    with patch.object(hp, "_get_client", return_value=client):
        r = hp.capture_honcho("user asked about X", role="user", source="claude-code", session_id="s1")
    assert r.ok
    session.add_messages.assert_called_once()  # one write for the user turn


def test_recall_uses_dialectic_chat():
    from quad_memory import honcho_plane as hp
    client, human, assistant, session = _fake_client()
    with patch.object(hp, "_get_client", return_value=client):
        mems = hp.recall_honcho("what does Jack prefer for secrets?", limit=1)
    assistant.chat.assert_called_once()
    assert mems and mems[0].plane == "honcho" and "SOPS" in mems[0].content


def test_health_fail_open_when_unreachable():
    from quad_memory import honcho_plane as hp
    with patch.object(hp, "_get_client", side_effect=RuntimeError("down")):
        r = hp.honcho_health()
    assert r.ok is False and "down" in r.detail


def test_capture_rejects_secret():
    from quad_memory import honcho_plane as hp
    client, human, assistant, session = _fake_client()
    with patch.object(hp, "_get_client", return_value=client):
        r = hp.capture_honcho("export OPENAI_API_KEY=sk-abcdef1234567890abcdef",
                              role="user", source="claude-code", session_id="s1")
    assert r.ok is False
    session.add_messages.assert_not_called()
