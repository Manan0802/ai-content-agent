from integrations.groq_client import GroqClient


def test_complete_passes_messages_and_returns_text(monkeypatch):
    captured = {}

    def fake_chat(messages, json_mode):
        captured["messages"] = messages
        captured["json_mode"] = json_mode
        return "hello world"

    c = GroqClient(api_key="x", model="m")
    monkeypatch.setattr(c, "_chat", fake_chat)
    out = c.complete(system="sys", user="usr", json_mode=True)
    assert out == "hello world"
    assert captured["messages"][0]["role"] == "system"
    assert captured["messages"][0]["content"] == "sys"
    assert captured["messages"][1]["role"] == "user"
    assert captured["json_mode"] is True
