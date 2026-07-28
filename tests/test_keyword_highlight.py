"""The reference crime accounts colour ONE word per card — the word carrying the threat or the
reveal. It is the cheapest way to stop a line of burned-in text reading like a subtitle, and it
tells the eye where to land in the ~2.5s the card is on screen.
"""
from agents.composition_writer import composition_writer_node
from orchestrator.state import new_state


def _render(tmp_path, segments):
    s = new_state("crime", "semi_auto", "hindi", "short", [])
    s["script"] = {"title": "T", "segments": segments}
    s["visual_assets"] = [{"scene_number": g["scene_number"], "image_url": "i.jpg",
                           "tier": "broll"} for g in segments]
    composition_writer_node(s, project_dir=str(tmp_path), disclosure_duration_sec=0)
    return (tmp_path / "index.html").read_text()


def test_the_highlight_word_is_wrapped_so_it_can_be_coloured(tmp_path):
    html = _render(tmp_path, [{"scene_number": 1, "duration_sec": 3,
                               "dialogue": "लाश तीन दिन पुरानी थी", "highlight": "लाश"}])
    assert '<span class="hl">लाश</span> तीन दिन पुरानी थी' in html
    assert ".hl {" in html                      # and the class is actually styled


def test_only_the_first_occurrence_is_highlighted(tmp_path):
    html = _render(tmp_path, [{"scene_number": 1, "duration_sec": 3,
                               "dialogue": "पैसा ही पैसा", "highlight": "पैसा"}])
    assert html.count('<span class="hl">') == 1


def test_a_card_without_a_highlight_renders_plain(tmp_path):
    html = _render(tmp_path, [{"scene_number": 1, "duration_sec": 3, "dialogue": "कुछ नहीं"}])
    assert "<span class=\"hl\">" not in html
    assert "कुछ नहीं" in html


def test_a_highlight_that_is_not_in_the_line_is_ignored(tmp_path):
    html = _render(tmp_path, [{"scene_number": 1, "duration_sec": 3,
                               "dialogue": "दरवाज़ा खुला था", "highlight": "चाबी"}])
    assert "<span class=\"hl\">" not in html
    assert "दरवाज़ा खुला था" in html
