from orchestrator.state import new_state
from agents.visuals import visuals_node


LONG_HINDI = ("एक लो-लाइट, ग्रे और ब्लू टोन में फिल्माया गया दृश्य, जिसमें डरावनी और तनावपूर्ण "
              "माहौल है. एक सुनसान फ्लैट का दरवाजा, अज्ञात महिला खड़ी है")


class FakeFal:
    def generate_hero_image(self, prompt, ref):
        return "https://image.pollinations.ai/prompt/" + prompt.replace(" ", "%20")

    def generate_broll_image(self, prompt):
        return "https://image.pollinations.ai/prompt/" + prompt.replace(" ", "%20")


def _state():
    s = new_state("horror", "semi_auto", "hindi", "short", [], format_profile="serial_75s")
    s["script"] = {"segments": [
        {"scene_number": 1, "visual_direction": LONG_HINDI, "character_visible": False},
        {"scene_number": 2, "visual_direction": LONG_HINDI + " दूसरा", "character_visible": False},
    ]}
    return s


def test_images_are_downloaded_to_short_local_paths(tmp_path):
    def fake_fetch(url, dest):
        with open(dest, "wb") as f:
            f.write(b"\x89PNG" + b"\x00" * 512)

    out = visuals_node(_state(), fal=FakeFal(), character_ref_url="",
                       project_dir=str(tmp_path), fetch=fake_fetch, pace_sec=0)

    for a in out["visual_assets"]:
        # composition references a short RELATIVE path, never the giant encoded URL
        assert a["image_url"].startswith("images/")
        assert len(a["image_url"]) < 40
        assert (tmp_path / a["image_url"]).exists()
        # HyperFrames' downloader hit the OS 255-byte filename limit on encoded Hindi URLs
        assert len(a["image_url"].encode("utf-8")) < 255


def test_remote_url_is_kept_when_download_fails(tmp_path):
    def failing_fetch(url, dest):
        raise RuntimeError("429 rate limited")

    out = visuals_node(_state(), fal=FakeFal(), character_ref_url="",
                       project_dir=str(tmp_path), fetch=failing_fetch, pace_sec=0)
    # falls back to the remote URL rather than losing the scene entirely
    assert out["visual_assets"][0]["image_url"].startswith("http")
    assert any("image download" in e for e in out["errors"])


def test_without_project_dir_behaviour_is_unchanged(tmp_path):
    out = visuals_node(_state(), fal=FakeFal(), character_ref_url="")
    assert out["visual_assets"][0]["image_url"].startswith("http")
    assert out["errors"] == []
