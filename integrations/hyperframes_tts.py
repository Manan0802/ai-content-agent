import os
import sys
import subprocess


class HyperFramesTTS:
    def __init__(self, voice: str = "af_heart", runner=subprocess.run, python_exe: str | None = None):
        self._voice = voice
        self._run = runner
        # HyperFrames' Kokoro TTS shells out to Python for kokoro-onnx + soundfile.
        # Point it at the interpreter running us (our venv has those installed).
        self._python = python_exe or sys.executable

    def synthesize(self, text: str, output_path: str, voice: str | None = None) -> str:
        # The published `hyperframes tts` CLI is the local Kokoro-only build:
        # it has no --provider flag (Kokoro is the only engine). Voice via --voice.
        cmd = ["npx", "hyperframes", "tts", text, "-o", output_path,
               "--voice", voice or self._voice]
        env = {**os.environ, "HYPERFRAMES_PYTHON": self._python}
        result = self._run(cmd, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            raise RuntimeError(f"hyperframes tts failed: {result.stderr}")
        # The CLI exits 0 even when synthesis fails (e.g. missing kokoro-onnx),
        # so verify a real audio file was actually produced.
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError(f"hyperframes tts produced no audio: {result.stdout[-300:]}")
        return output_path
