from orchestrator.state import new_state
from agents.voiceover import voiceover_node


class FakeTTS:
    def __init__(self):
        self.calls = []

    def synthesize(self, text, output_path):
        self.calls.append((text, output_path))
        return output_path


def test_voiceover_writes_one_file_per_segment(tmp_path):
    s = new_state("horror", "semi_auto", "hinglish", "short", ["script"])
    s["script"] = {"segments": [
        {"scene_number": 1, "voiceover_text": "line one"},
        {"scene_number": 2, "voiceover_text": "line two"},
    ]}
    tts = FakeTTS()
    out = voiceover_node(s, tts=tts, output_dir=str(tmp_path))
    assert len(out["audio_assets"]) == 2
    assert out["audio_assets"][0]["scene_number"] == 1
    assert len(tts.calls) == 2


def test_voiceover_synthesizes_disclosure_line_when_provided(tmp_path):
    s = new_state("horror", "semi_auto", "hinglish", "short", ["script"])
    s["script"] = {"segments": [{"scene_number": 1, "voiceover_text": "line one"}]}
    tts = FakeTTS()
    out = voiceover_node(s, tts=tts, output_dir=str(tmp_path),
                         disclosure_text="This video uses AI-generated voice and visuals.")
    assert out["disclosure_audio_path"].endswith("disclosure.wav")
    assert len(tts.calls) == 2  # 1 segment + 1 disclosure line
