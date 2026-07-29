"""How dialogue appears on screen, decided by what the reference reels actually do.

Measured across four reels downloaded and inspected 2026-07-29:

    official_sheru_empire   98,093 likes   voiceover, NO dialogue text, small Part badge
    tech_dhamal             32,257 likes   voiceover, NO dialogue text, small Part badge
    story_hub_life           9,086 likes   music,     speech bubbles pointing at the speaker
    dark_crime_8             1,557 likes   music,     large top banner, multi-colour words

The two biggest performers burn no dialogue at all — the voice carries it, and a giant caption
over a narrated scene reads as amateur. Where text IS the only channel (music mode, no voice),
bubbles beat a banner by roughly 6x.

Our own videos were built like the 1,557-like one.
"""
import pytest
from agents.composition_writer import composition_writer_node, text_mode_for
from orchestrator.state import new_state


def _render(tmp_path, fmt="serial_75s", text_mode=None, speaker=None, chars=None):
    s = new_state("crime", "semi_auto", "hindi", "short", [], format_profile=fmt)
    s["script"] = {"title": "T", "characters": chars or [], "segments": [
        {"scene_number": 1, "duration_sec": 3, "dialogue": "वो वापस आ गया", "speaker": speaker},
    ]}
    s["visual_assets"] = [{"scene_number": 1, "image_url": "i.jpg", "tier": "broll"}]
    kw = {"text_mode": text_mode} if text_mode else {}
    composition_writer_node(s, project_dir=str(tmp_path), disclosure_duration_sec=0, **kw)
    return (tmp_path / "index.html").read_text()


@pytest.mark.parametrize("fmt,expected", [
    ("serial_75s", "banner"),    # music mode: text is the ONLY channel, it must be there
    ("montage_35s", "banner"),
    ("drama_50s", "none"),       # narrated: the voice carries it, like the 98K and 32K reels
    ("joke_10s", "none"),
])
def test_the_default_follows_whether_the_scene_has_a_voice(fmt, expected):
    assert text_mode_for(fmt) == expected


def test_an_unknown_format_keeps_the_text(tmp_path):
    """Better to show a caption we didn't need than to ship a silent video with no words."""
    assert text_mode_for("something-new") == "banner"


def test_a_narrated_video_carries_no_dialogue_banner(tmp_path):
    html = _render(tmp_path, fmt="drama_50s")
    assert "वो वापस आ गया" not in html
    assert 'class="dialogue"' not in html


def test_a_narrated_video_still_keeps_its_images_and_timing(tmp_path):
    html = _render(tmp_path, fmt="drama_50s")
    assert 'src="i.jpg"' in html
    assert 'data-duration="3.0"' in html


def test_a_music_video_still_burns_the_line(tmp_path):
    html = _render(tmp_path, fmt="serial_75s")
    assert "वो वापस आ गया" in html


def test_bubble_mode_renders_a_bubble_with_a_tail(tmp_path):
    html = _render(tmp_path, text_mode="bubble")
    assert 'class="bubble"' in html
    assert ".bubble::after" in html          # the tail
    assert "वो वापस आ गया" in html


def test_bubble_mode_replaces_the_banner_rather_than_adding_to_it(tmp_path):
    html = _render(tmp_path, text_mode="bubble")
    assert 'class="dialogue"' not in html


def test_an_explicit_mode_overrides_the_format_default(tmp_path):
    html = _render(tmp_path, fmt="drama_50s", text_mode="banner")
    assert "वो वापस आ गया" in html
