import pytest
from integrations.hyperframes_tts import HyperFramesTTS


class FakeResult:
    def __init__(self, returncode=0, stderr="", stdout=""):
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = stdout


def test_synthesize_calls_cli_and_verifies_output(tmp_path):
    out_path = str(tmp_path / "scene_1.wav")
    captured = {}

    def fake_run(cmd, capture_output, text, env=None):
        captured["cmd"] = cmd
        captured["env"] = env
        with open(out_path, "wb") as f:  # simulate the CLI writing audio
            f.write(b"\x00" * 100)
        return FakeResult(0)

    tts = HyperFramesTTS(voice="af_heart", runner=fake_run)
    out = tts.synthesize("Bhoot bangla real story", out_path)
    assert out == out_path
    assert captured["cmd"][:3] == ["npx", "hyperframes", "tts"]
    assert "--voice" in captured["cmd"] and "af_heart" in captured["cmd"]
    assert "--provider" not in captured["cmd"]  # published tts CLI has no --provider
    assert "HYPERFRAMES_PYTHON" in captured["env"]  # points TTS at our venv python


def test_synthesize_raises_on_nonzero_exit():
    def fake_run(cmd, capture_output, text, env=None):
        return FakeResult(1, stderr="boom")

    tts = HyperFramesTTS(runner=fake_run)
    with pytest.raises(RuntimeError):
        tts.synthesize("x", "out.wav")


def test_synthesize_raises_when_no_audio_despite_exit_zero(tmp_path):
    # The real CLI exits 0 even when synthesis fails — verify we catch that.
    def fake_run(cmd, capture_output, text, env=None):
        return FakeResult(0, stdout="Speech synthesis failed: kokoro-onnx not installed")

    tts = HyperFramesTTS(runner=fake_run)
    with pytest.raises(RuntimeError, match="produced no audio"):
        tts.synthesize("x", str(tmp_path / "missing.wav"))
