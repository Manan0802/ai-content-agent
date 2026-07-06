from orchestrator.state import new_state
from agents.visuals import visuals_node


class FakeFal:
    def generate_hero_image(self, prompt, ref):
        return f"hero:{prompt}"

    def generate_broll_image(self, prompt):
        return f"broll:{prompt}"


def _state_with_script():
    s = new_state("horror", "semi_auto", "hinglish", "short", ["script"])
    s["script"] = {"segments": [
        {"scene_number": 1, "visual_direction": "dark fort", "character_visible": True},
        {"scene_number": 2, "visual_direction": "old temple", "character_visible": False},
    ]}
    return s


def test_hero_scene_uses_hero_tier_when_ref_present():
    out = visuals_node(_state_with_script(), fal=FakeFal(), character_ref_url="https://x/ref.png")
    assert out["visual_assets"][0]["tier"] == "hero"
    assert out["visual_assets"][1]["tier"] == "broll"


def test_hero_scene_falls_back_to_broll_without_ref():
    out = visuals_node(_state_with_script(), fal=FakeFal(), character_ref_url="")
    assert out["visual_assets"][0]["tier"] == "broll"
