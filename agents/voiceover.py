import os
from orchestrator.state import ContentState
from integrations.hyperframes_tts import HyperFramesTTS


def voiceover_node(state: ContentState, tts: HyperFramesTTS, output_dir: str,
                   disclosure_text: str = "") -> ContentState:
    try:
        os.makedirs(output_dir, exist_ok=True)
        assets = []
        for seg in state["script"]["segments"]:
            path = os.path.join(output_dir, f"scene_{seg['scene_number']}.wav")
            tts.synthesize(seg["voiceover_text"], path)
            assets.append({"scene_number": seg["scene_number"], "audio_path": path})
        state["audio_assets"] = assets

        if disclosure_text:
            disclosure_path = os.path.join(output_dir, "disclosure.wav")
            tts.synthesize(disclosure_text, disclosure_path)
            state["disclosure_audio_path"] = disclosure_path
        else:
            state["disclosure_audio_path"] = ""
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"voiceover: {e}")
        state["audio_assets"] = []
        state["disclosure_audio_path"] = ""
    return state
