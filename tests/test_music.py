from modules.music import MOODS, mood_for_niche, pick_track


def _make_lib(tmp_path, mood, names):
    d = tmp_path / mood
    d.mkdir(parents=True, exist_ok=True)
    for n in names:
        (d / n).write_bytes(b"\x00" * 64)
    return d


def test_moods_cover_our_niches():
    assert set(MOODS) == {"dark", "emotional", "comedy", "devotional"}


def test_mood_for_niche_maps_known_niches():
    assert mood_for_niche("horror") == "dark"
    assert mood_for_niche("mythology") == "devotional"
    assert mood_for_niche("comedy") == "comedy"
    assert mood_for_niche("motivation") == "emotional"
    assert mood_for_niche("something-unknown") == "emotional"  # safe default


def test_pick_track_returns_a_file_from_the_mood_folder(tmp_path):
    _make_lib(tmp_path, "dark", ["a.mp3", "b.mp3"])
    t = pick_track("dark", str(tmp_path), seed="series-1")
    assert t is not None
    assert t.endswith((".mp3",))
    assert "/dark/" in t


def test_pick_track_is_deterministic_per_seed(tmp_path):
    _make_lib(tmp_path, "dark", ["a.mp3", "b.mp3", "c.mp3"])
    a = pick_track("dark", str(tmp_path), seed="series-1")
    b = pick_track("dark", str(tmp_path), seed="series-1")
    assert a == b                      # same series -> same track across all its parts


def test_different_seeds_can_pick_different_tracks(tmp_path):
    _make_lib(tmp_path, "dark", ["a.mp3", "b.mp3", "c.mp3", "d.mp3"])
    picks = {pick_track("dark", str(tmp_path), seed=f"s{i}") for i in range(12)}
    assert len(picks) > 1


def test_missing_mood_folder_returns_none_not_crash(tmp_path):
    assert pick_track("dark", str(tmp_path), seed="x") is None


def test_empty_mood_folder_returns_none(tmp_path):
    _make_lib(tmp_path, "dark", [])
    assert pick_track("dark", str(tmp_path), seed="x") is None


def test_non_audio_files_are_ignored(tmp_path):
    _make_lib(tmp_path, "dark", ["notes.txt", "cover.jpg"])
    assert pick_track("dark", str(tmp_path), seed="x") is None


# --- voiceover_node integration: music mode picks BGM, narrated mode doesn't ---

from orchestrator.state import new_state          # noqa: E402
from agents.voiceover import voiceover_node       # noqa: E402


class _FakeTTS:
    def __init__(self):
        self.calls = []

    def synthesize(self, text, output_path, voice=None):
        self.calls.append(text)
        return output_path


def _music_state(niche="horror", series_id=""):
    s = new_state(niche, "semi_auto", "hindi", "short", [], format_profile="serial_75s")
    s["series_id"] = series_id
    s["script"] = {"characters": [], "segments": [
        {"scene_number": 1, "duration_sec": 5, "dialogue": "line"}]}
    return s


def test_music_mode_selects_a_bgm_track(tmp_path):
    _make_lib(tmp_path, "dark", ["scary.mp3"])
    out = voiceover_node(_music_state(), tts=_FakeTTS(), output_dir=str(tmp_path / "aud"),
                         music_dir=str(tmp_path))
    assert out["bgm_path"].endswith("scary.mp3")
    assert out["audio_assets"] == []


def test_music_mode_same_series_gets_same_track(tmp_path):
    _make_lib(tmp_path, "dark", ["a.mp3", "b.mp3", "c.mp3"])
    p1 = voiceover_node(_music_state(series_id="ser-9"), tts=_FakeTTS(),
                        output_dir=str(tmp_path / "a"), music_dir=str(tmp_path))["bgm_path"]
    p2 = voiceover_node(_music_state(series_id="ser-9"), tts=_FakeTTS(),
                        output_dir=str(tmp_path / "b"), music_dir=str(tmp_path))["bgm_path"]
    assert p1 == p2


def test_music_mode_without_tracks_notes_it_and_stays_silent(tmp_path):
    out = voiceover_node(_music_state(), tts=_FakeTTS(), output_dir=str(tmp_path / "aud"),
                         music_dir=str(tmp_path))
    assert out["bgm_path"] == ""
    assert any("no dark track" in e for e in out["errors"])


def test_narrated_mode_does_not_set_bgm(tmp_path):
    s = new_state("horror", "semi_auto", "hindi", "short", [], format_profile="drama_50s")
    s["script"] = {"characters": [{"id": "a", "voice_hint": "male"}], "segments": [
        {"scene_number": 1, "duration_sec": 5, "speaker": "a", "dialogue": "hi"}]}
    out = voiceover_node(s, tts=_FakeTTS(), output_dir=str(tmp_path / "aud"),
                         music_dir=str(tmp_path))
    assert out.get("bgm_path", "") == ""
    assert len(out["audio_assets"]) == 1
