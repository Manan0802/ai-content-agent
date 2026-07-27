from orchestrator.state import new_state
from agents.composition_writer import composition_writer_node


def test_composition_writer_produces_valid_contract_html(tmp_path):
    s = new_state("horror", "semi_auto", "hinglish", "short", ["script"])
    s["script"] = {"title": "Cursed Village", "segments": [
        {"scene_number": 1, "duration_sec": 5, "voiceover_text": "v1"},
        {"scene_number": 2, "duration_sec": 7, "voiceover_text": "v2"},
    ]}
    s["visual_assets"] = [
        {"scene_number": 1, "image_url": "https://x/a.png", "tier": "hero"},
        {"scene_number": 2, "image_url": "https://x/b.png", "tier": "broll"},
    ]
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    a1, a2 = audio_dir / "scene_1.wav", audio_dir / "scene_2.wav"
    a1.write_bytes(b"x")
    a2.write_bytes(b"x")
    s["audio_assets"] = [
        {"scene_number": 1, "audio_path": str(a1)},
        {"scene_number": 2, "audio_path": str(a2)},
    ]
    disclosure = audio_dir / "disclosure.wav"
    disclosure.write_bytes(b"x")
    s["disclosure_audio_path"] = str(disclosure)

    out = composition_writer_node(s, project_dir=str(tmp_path), disclosure_duration_sec=3.0)
    html = (tmp_path / "index.html").read_text()

    assert out["composition_path"] == str(tmp_path / "index.html")
    assert 'data-duration="15.0"' in html          # 3 (disclosure) + 5 + 7
    assert html.count('class="clip"') == 3         # disclosure intro + 2 segments
    assert html.count("<audio") == 3                # disclosure + 2 segments
    assert 'id="ai-label"' in html                  # persistent visible label
    # The label covers every scene, but starts after the disclosure card — during the card it
    # would sit on top of the full-frame disclosure text, which `hyperframes check` rejects as
    # overlapping text (and the card already says the same thing).
    assert 'id="ai-label" class="clip ai-label" data-start="3.0" data-duration="12.0"' in html
    # scene 1 must start AFTER the disclosure intro, not at 0
    assert 'data-start="3.0" data-duration="5.0"' in html
    # audio must not be nested inside a clip section
    assert html.split("<audio")[0].count("</section>") >= 1


def test_composition_writer_without_disclosure_audio_starts_at_zero(tmp_path):
    s = new_state("horror", "semi_auto", "hinglish", "short", ["script"])
    s["script"] = {"title": "T", "segments": [
        {"scene_number": 1, "duration_sec": 5, "voiceover_text": "v1"},
    ]}
    s["disclosure_audio_path"] = ""
    out = composition_writer_node(s, project_dir=str(tmp_path))
    html = (tmp_path / "index.html").read_text()
    assert 'data-start="0.0" data-duration="5.0"' in html
    assert html.count('class="clip"') == 1  # no disclosure intro clip
