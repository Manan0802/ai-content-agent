"""Every serial in the reference set closes by telling you there is a next part — `r1_sheru`
ends on "अब असली कहाणी शुरू होगी" spoken inside the story, and the caption stacks the ask on top.
The video itself needs to say it too, because a viewer who watched to the end is the one most
likely to follow, and they should not have to open the caption to learn Part 2 exists.
"""
from agents.composition_writer import composition_writer_node
from orchestrator.state import new_state


def _render(tmp_path, outro=None):
    s = new_state("crime", "semi_auto", "hindi", "short", [])
    s["script"] = {"title": "T", "segments": [
        {"scene_number": 1, "duration_sec": 3, "dialogue": "एक"},
        {"scene_number": 2, "duration_sec": 3, "dialogue": "दो"},
    ]}
    s["visual_assets"] = [{"scene_number": n, "image_url": "i.jpg", "tier": "broll"}
                          for n in (1, 2)]
    if outro is not None:
        s["outro"] = outro
    composition_writer_node(s, project_dir=str(tmp_path), disclosure_duration_sec=0)
    return (tmp_path / "index.html").read_text()


def test_the_outro_card_appears_after_the_last_scene(tmp_path):
    html = _render(tmp_path, {"text": "PART 2 कल", "duration_sec": 2.5})
    assert 'id="outro"' in html
    # scenes occupy 0-6s, so the outro must start at 6 and the video must run to 8.5
    assert 'id="outro" class="clip outro" data-start="6.0" data-duration="2.5"' in html
    assert 'data-duration="8.5"' in html            # root duration grew to include it


def test_the_outro_text_is_rendered(tmp_path):
    html = _render(tmp_path, {"text": "PART 2 कल आ रहा है"})
    assert "PART 2 कल आ रहा है" in html


def test_no_outro_means_no_card_and_no_extra_time(tmp_path):
    html = _render(tmp_path)
    assert 'id="outro"' not in html
    assert 'data-duration="6.0"' in html


def test_the_outro_animates_so_the_timeline_never_goes_static(tmp_path):
    """An empty stretch of timeline fails `hyperframes check` with sweep_static."""
    html = _render(tmp_path, {"text": "PART 2"})
    assert '#outro' in html.split("<script>")[-1]
