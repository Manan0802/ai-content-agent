from integrations.youtube_client import YouTubeClient


def test_is_configured_true_when_all_creds_present():
    c = YouTubeClient(client_id="a", client_secret="b", refresh_token="c")
    assert c.is_configured() is True


def test_is_configured_false_when_a_cred_missing():
    assert YouTubeClient(client_id="a", client_secret="b", refresh_token=None).is_configured() is False
    assert YouTubeClient(client_id=None, client_secret="b", refresh_token="c").is_configured() is False


def test_upload_video_builds_body_and_returns_id(monkeypatch):
    captured = {}

    def fake_insert(body, file_path):
        captured["body"] = body
        captured["file_path"] = file_path
        return {"id": "abc123"}

    c = YouTubeClient(client_id="a", client_secret="b", refresh_token="c")
    monkeypatch.setattr(c, "_insert", fake_insert)
    vid = c.upload_video(
        file_path="outputs/x/render/final.mp4",
        title="Cursed Station",
        description="scary stuff #Shorts",
        tags=["horror", "india"],
        privacy="unlisted",
    )
    assert vid == "abc123"
    assert captured["file_path"] == "outputs/x/render/final.mp4"
    body = captured["body"]
    assert body["snippet"]["title"] == "Cursed Station"
    assert body["snippet"]["description"] == "scary stuff #Shorts"
    assert body["snippet"]["tags"] == ["horror", "india"]
    assert body["status"]["privacyStatus"] == "unlisted"
