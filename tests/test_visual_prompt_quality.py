"""The image prompt is the single biggest driver of whether a video looks like the reference
reels or like stock slop. Two things were broken:

1. `visual_direction` came back in Hindi, because the whole prompt says "write in Hindi".
   Image models are trained on English captions, so a Devanagari prompt produces something
   unrelated — one run asked for a cursed village at midnight and got a photo of a puppy.
2. A single (non-series) job had no locked art direction at all, so every scene in the same
   video looked like a different show.
"""
from prompts.script_prompts import script_system_prompt
from modules.style import style_for_niche
from agents.visuals import visuals_node
from orchestrator.state import new_state


class FakeFal:
    def __init__(self):
        self.prompts = []

    def generate_broll_image(self, prompt):
        self.prompts.append(prompt)
        return "https://x/i.png"

    def generate_hero_image(self, prompt, ref):
        self.prompts.append(prompt)
        return "https://x/i.png"


def test_visual_direction_must_be_written_in_english_even_for_a_hindi_script():
    p = script_system_prompt("horror", "hindi")
    assert "visual_direction" in p
    lower = p.lower()
    # the language rule above it says "write in Hindi" — visuals must be carved out explicitly
    assert "english" in lower


def test_every_niche_has_a_locked_cinematic_look():
    for niche in ["horror", "crime", "facts"]:
        look = style_for_niche(niche)
        assert len(look) > 20          # a real art direction, not a one-word label


def test_unknown_niche_still_gets_a_usable_look():
    assert len(style_for_niche("something-we-never-planned-for")) > 20


def test_a_single_job_falls_back_to_the_niche_look_so_scenes_match_each_other(tmp_path):
    s = new_state("horror", "semi_auto", "hindi", "short", [])
    s["script"] = {"segments": [
        {"scene_number": 1, "visual_direction": "abandoned house at night"},
        {"scene_number": 2, "visual_direction": "a broken window"},
    ]}
    fal = FakeFal()
    visuals_node(s, fal=fal, character_ref_url="", project_dir=str(tmp_path),
                 fetch=lambda u, d: open(d, "wb").write(b"x" * 2048), pace_sec=0)

    look = style_for_niche("horror")
    assert all(look in p for p in fal.prompts)     # same locked look on every scene
    assert "abandoned house at night" in fal.prompts[0]


def test_an_explicit_series_style_still_wins_over_the_niche_default(tmp_path):
    s = new_state("horror", "semi_auto", "hindi", "short", [])
    s["script"] = {"segments": [{"scene_number": 1, "visual_direction": "a door"}]}
    fal = FakeFal()
    visuals_node(s, fal=fal, character_ref_url="", style_prompt="1970s Bollywood film grain",
                 project_dir=str(tmp_path),
                 fetch=lambda u, d: open(d, "wb").write(b"x" * 2048), pace_sec=0)

    assert "1970s Bollywood film grain" in fal.prompts[0]
    assert style_for_niche("horror") not in fal.prompts[0]
