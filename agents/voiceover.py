import os
from orchestrator.state import ContentState
from integrations.hyperframes_tts import HyperFramesTTS
from modules.formats import get_format
from modules.voices import assign_voices
from modules.music import mood_for_niche, pick_track


def _audio_mode(state: ContentState) -> str:
    fp = state.get("format_profile")
    if not fp:
        return "narrated"
    try:
        return get_format(fp).audio_mode
    except ValueError:
        return "narrated"


def _line_of(seg: dict) -> str:
    # v2 scripts use `dialogue` + `speaker`; Phase-1 scripts used `voiceover_text`
    return seg.get("dialogue") or seg.get("voiceover_text") or ""


def voiceover_node(state: ContentState, tts: HyperFramesTTS, output_dir: str,
                   disclosure_text: str = "", music_dir: str = "",
                   bgm_mode: str = "baked") -> ContentState:
    try:
        # Music-mode formats (thriller/nostalgia) have NO voiceover at all — a BGM track plays
        # and the dialogue is burned on screen. Matches shadow_files0 / realistic_crime.
        if _audio_mode(state) == "music":
            state["audio_assets"] = []
            state["disclosure_audio_path"] = ""
            state["voice_map"] = {}
            if music_dir and bgm_mode == "baked":
                mood = mood_for_niche(state.get("niche", ""))
                seed = state.get("series_id") or state.get("job_id", "")
                track = pick_track(mood, music_dir, seed=seed)
                state["bgm_path"] = track or ""
                if not track:
                    state.setdefault("errors", []).append(
                        f"music: no {mood} track in {music_dir} — rendering silent"
                    )
            else:
                state["bgm_path"] = ""
            return state

        os.makedirs(output_dir, exist_ok=True)
        voice_map = assign_voices(state.get("script", {}).get("characters", []))
        state["voice_map"] = voice_map

        assets = []
        for seg in state["script"]["segments"]:
            path = os.path.join(output_dir, f"scene_{seg['scene_number']}.wav")
            tts.synthesize(_line_of(seg), path, voice=voice_map.get(seg.get("speaker")))
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
