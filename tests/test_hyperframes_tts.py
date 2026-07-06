import pytest
from integrations.hyperframes_tts import HyperFramesTTS


class FakeResult:
    def __init__(self, returncode=0, stderr=""):
        self.returncode = returncode
        self.stderr = stderr


def test_synthesize_calls_cli_with_kokoro_pinned():
    captured = {}

    def fake_run(cmd, capture_output, text):
        captured["cmd"] = cmd
        return FakeResult(0)

    tts = HyperFramesTTS(voice="af_heart", runner=fake_run)
    out = tts.synthesize("Bhoot bangla real story", "out/scene_1.wav")
    assert out == "out/scene_1.wav"
    assert captured["cmd"][:3] == ["npx", "hyperframes", "tts"]
    assert "--provider" in captured["cmd"] and "kokoro" in captured["cmd"]
    assert "--voice" in captured["cmd"] and "af_heart" in captured["cmd"]


def test_synthesize_raises_on_nonzero_exit():
    def fake_run(cmd, capture_output, text):
        return FakeResult(1, "boom")

    tts = HyperFramesTTS(runner=fake_run)
    with pytest.raises(RuntimeError):
        tts.synthesize("x", "out.wav")
