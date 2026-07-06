import subprocess


class HyperFramesTTS:
    def __init__(self, voice: str = "af_heart", runner=subprocess.run):
        self._voice = voice
        self._run = runner

    def synthesize(self, text: str, output_path: str) -> str:
        cmd = ["npx", "hyperframes", "tts", text, "-o", output_path,
               "--provider", "kokoro", "--voice", self._voice]
        result = self._run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"hyperframes tts failed: {result.stderr}")
        return output_path
