from orchestrator.state import new_state
from agents.uploader import uploader_node


class FakeYouTube:
    def __init__(self, configured=True):
        self._configured = configured
        self.calls = []

    def is_configured(self):
        return self._configured

    def upload_video(self, file_path, title, description, tags, privacy="unlisted"):
        self.calls.append({"file_path": file_path, "title": title,
                           "description": description, "tags": tags, "privacy": privacy})
        return "vid123"


class ApproveNotifier:
    def ask_approval(self, title, preview):
        return "approve"


class RejectNotifier:
    def ask_approval(self, title, preview):
        return "reject"


def _ready_state(checkpoints=("publish",)):
    s = new_state("horror", "semi_auto", "hinglish", "short", list(checkpoints))
    s["status"] = "media_complete"
    s["render_output_path"] = "outputs/x/render/final.mp4"
    s["script"] = {"title": "Cursed Station", "hook": "Raat ko yahan kuch hota hai",
                   "hashtags": ["#horror", "#india"]}
    return s


def test_publishes_on_approval():
    yt = FakeYouTube(configured=True)
    out = uploader_node(_ready_state(), youtube=yt, notifier=ApproveNotifier())
    assert out["status"] == "published"
    assert out["youtube_video_id"] == "vid123"
    assert out["youtube_url"] == "https://youtu.be/vid123"
    # #Shorts must be in the description (that's what marks it a Short)
    assert "#Shorts" in yt.calls[0]["description"]
    assert yt.calls[0]["title"] == "Cursed Station"
    assert yt.calls[0]["privacy"] == "unlisted"


def test_reject_keeps_media_complete_not_published():
    yt = FakeYouTube(configured=True)
    out = uploader_node(_ready_state(), youtube=yt, notifier=RejectNotifier())
    assert out["status"] == "media_complete"
    assert out.get("youtube_video_id", "") == ""
    assert yt.calls == []  # nothing uploaded


def test_unconfigured_skips_cleanly():
    yt = FakeYouTube(configured=False)
    out = uploader_node(_ready_state(), youtube=yt, notifier=ApproveNotifier())
    assert out["status"] == "media_complete"
    assert yt.calls == []
    assert any("not configured" in e for e in out["errors"])


def test_no_video_skips():
    s = _ready_state()
    s["render_output_path"] = ""
    out = uploader_node(s, youtube=FakeYouTube(True), notifier=ApproveNotifier())
    assert out["status"] == "media_complete"


def test_failed_state_untouched():
    s = _ready_state()
    s["status"] = "failed"
    out = uploader_node(s, youtube=FakeYouTube(True), notifier=ApproveNotifier())
    assert out["status"] == "failed"


def test_upload_error_does_not_lose_video():
    class BoomYouTube(FakeYouTube):
        def upload_video(self, *a, **k):
            raise RuntimeError("quota exceeded")
    out = uploader_node(_ready_state(), youtube=BoomYouTube(True), notifier=ApproveNotifier())
    assert out["status"] == "media_complete"  # video safe, not failed
    assert any("quota exceeded" in e for e in out["errors"])
