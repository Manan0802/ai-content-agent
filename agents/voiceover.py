import os
import subprocess
from orchestrator.state import ContentState
from integrations.hyperframes_tts import HyperFramesTTS
from modules.formats import get_format
from modules.voices import assign_voices
from modules.music import mood_for_niche, pick_track
from modules.timing import reading_duration


def _audio_mode(state: ContentState) -> str:
    fp = state.get("format_profile")
    if not fp:
        return "narrated"
    try:
        return get_format(fp).audio_mode
    except ValueError:
        return "narrated"


def _probe_duration(path: str) -> float:
    """Real length of an audio file, in seconds."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def _line_of(seg: dict) -> str:
    # v2 scripts use `dialogue` + `speaker`; Phase-1 scripts used `voiceover_text`
    return seg.get("dialogue") or seg.get("voiceover_text") or ""


def voiceover_node(state: ContentState, tts: HyperFramesTTS, output_dir: str,
                   disclosure_text: str = "", music_dir: str = "",
                   bgm_mode: str = "baked", probe=_probe_duration,
                   tail_sec: float = 0.25) -> ContentState:
    try:
        # Music-mode formats (thriller/nostalgia) have NO voiceover at all — a BGM track plays
        # and the dialogue is burned on screen. Matches shadow_files0 / realistic_crime.
        if _audio_mode(state) == "music":
            state["audio_assets"] = []
            state["disclosure_audio_path"] = ""
            state["voice_map"] = {}
            # No speech to measure here, so the card is timed by how long it takes to READ —
            # otherwise a 3-word and a 14-word line both sit for whatever the LLM guessed.
            for seg in state.get("script", {}).get("segments", []):
                seg["duration_sec"] = reading_duration(_line_of(seg))
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

            # The script's duration_sec is the LLM guessing how long its own line takes.
            # It is always wrong, which is what makes the image cut mid-sentence or sit in
            # dead air. Re-time the scene from the ACTUAL speech instead.
            entry = {"scene_number": seg["scene_number"], "audio_path": path}
            try:
                real = probe(path)
                entry["duration_sec"] = real
                seg["duration_sec"] = round(real + tail_sec, 2)   # + a short breath
            except Exception as e:  # noqa: BLE001 - keep the script's guess if we can't measure
                state.setdefault("errors", []).append(
                    f"voiceover: could not measure duration for scene {seg['scene_number']}: {e}"
                )
            assets.append(entry)
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
