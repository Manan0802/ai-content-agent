from orchestrator.state import new_state
from agents.composition_writer import composition_writer_node


def _base(fmt, tmp_path, with_audio=True):
    s = new_state("horror", "semi_auto", "hindi", "short", [], format_profile=fmt)
    s["script"] = {
        "title": "कर्ज़",
        "characters": [{"id": "sheru", "name": "शेरू"}, {"id": "kalu", "name": "कालू"}],
        "segments": [
            {"scene_number": 1, "duration_sec": 5, "speaker": "sheru",
             "dialogue": "मन्ने कुछ दिन गरीब बनके जीणा से", "visual_direction": "v1"},
            {"scene_number": 2, "duration_sec": 5, "speaker": "kalu",
             "dialogue": "जैसा तु कहे शेरू भाई", "visual_direction": "v2"},
        ],
    }
    s["visual_assets"] = [
        {"scene_number": 1, "image_url": "https://x/a.png", "tier": "broll"},
        {"scene_number": 2, "image_url": "https://x/b.png", "tier": "broll"},
    ]
    if with_audio:
        ad = tmp_path / "aud"
        ad.mkdir(parents=True, exist_ok=True)
        s["audio_assets"] = []
        for n in (1, 2):
            f = ad / f"scene_{n}.wav"
            f.write_bytes(b"\x00" * 32)
            s["audio_assets"].append({"scene_number": n, "audio_path": str(f)})
    return s


def test_narrated_mode_has_per_segment_audio(tmp_path):
    s = _base("drama_50s", tmp_path)
    composition_writer_node(s, project_dir=str(tmp_path))
    html = (tmp_path / "index.html").read_text()
    assert html.count("<audio") == 2          # one per segment
    assert 'id="bgm"' not in html


def test_music_mode_has_single_bgm_and_no_per_scene_audio(tmp_path):
    s = _base("serial_75s", tmp_path, with_audio=False)
    bgm = tmp_path / "track.mp3"
    bgm.write_bytes(b"\x00" * 64)
    s["bgm_path"] = str(bgm)
    composition_writer_node(s, project_dir=str(tmp_path))
    html = (tmp_path / "index.html").read_text()
    assert html.count("<audio") == 1          # exactly the BGM
    assert 'id="bgm"' in html
    assert 'data-duration="10.0"' in html     # BGM spans whole video (5+5)


def test_dialogue_is_rendered_as_onscreen_text(tmp_path):
    s = _base("serial_75s", tmp_path, with_audio=False)
    composition_writer_node(s, project_dir=str(tmp_path))
    html = (tmp_path / "index.html").read_text()
    assert "मन्ने कुछ दिन गरीब बनके जीणा से" in html
    assert "जैसा तु कहे शेरू भाई" in html


def test_speaker_name_shown_when_multiple_characters(tmp_path):
    s = _base("serial_75s", tmp_path, with_audio=False)
    composition_writer_node(s, project_dir=str(tmp_path))
    html = (tmp_path / "index.html").read_text()
    assert "शेरू" in html and "कालू" in html


def test_part_badge_only_when_part_of_a_series(tmp_path):
    s = _base("serial_75s", tmp_path, with_audio=False)
    composition_writer_node(s, project_dir=str(tmp_path))
    assert 'id="part-badge"' not in (tmp_path / "index.html").read_text()

    s2 = _base("serial_75s", tmp_path, with_audio=False)
    s2["part_number"] = 3
    composition_writer_node(s2, project_dir=str(tmp_path))
    html = (tmp_path / "index.html").read_text()
    assert 'id="part-badge"' in html
    assert "PART 3" in html


def test_hyperframes_contract_still_holds(tmp_path):
    # the rules that bit us live in Phase 2: root needs data-start, every timed element
    # needs class="clip" and an id
    s = _base("serial_75s", tmp_path, with_audio=False)
    s["part_number"] = 2
    composition_writer_node(s, project_dir=str(tmp_path))
    html = (tmp_path / "index.html").read_text()
    assert 'id="root"' in html and 'data-start="0"' in html
    assert 'id="ai-label" class="clip ai-label"' in html
    assert 'id="part-badge" class="clip' in html
