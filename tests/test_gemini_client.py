import os
from integrations.gemini_client import GeminiImageClient


class FakePart:
    def __init__(self, data):
        self.inline_data = type("D", (), {"data": data})()


def _fake_generate(png=b"\x89PNG" + b"\x00" * 4096):
    calls = []

    def gen(model, contents, aspect_ratio, ref_bytes):
        calls.append({"model": model, "contents": contents,
                      "aspect_ratio": aspect_ratio, "ref_bytes": ref_bytes})
        return png

    return gen, calls


def test_broll_writes_image_and_returns_file_url(tmp_path, monkeypatch):
    gen, calls = _fake_generate()
    c = GeminiImageClient(api_key="k", out_dir=str(tmp_path))
    monkeypatch.setattr(c, "_generate", gen)

    url = c.generate_broll_image("a dark alley at night")
    assert url.startswith("file://")
    path = url[len("file://"):]
    assert os.path.exists(path) and os.path.getsize(path) > 1024
    assert calls[0]["aspect_ratio"] == "9:16"          # vertical, always
    assert calls[0]["ref_bytes"] is None               # no reference for b-roll
    assert "dark alley" in calls[0]["contents"]


def test_hero_passes_reference_image_for_character_lock(tmp_path, monkeypatch):
    ref = tmp_path / "ref.jpg"
    ref.write_bytes(b"\xff\xd8REF" + b"\x00" * 2048)

    gen, calls = _fake_generate()
    c = GeminiImageClient(api_key="k", out_dir=str(tmp_path))
    monkeypatch.setattr(c, "_generate", gen)
    monkeypatch.setattr(c, "_load_reference", lambda url: ref.read_bytes())

    url = c.generate_hero_image("the hero walks in", f"file://{ref}")
    assert url.startswith("file://")
    # this is the whole point of using Gemini: the reference image goes to the model
    assert calls[0]["ref_bytes"] == ref.read_bytes()


def test_is_configured_reflects_key():
    assert GeminiImageClient(api_key="k").is_configured() is True
    assert GeminiImageClient(api_key=None).is_configured() is False


def test_each_call_writes_a_distinct_file(tmp_path, monkeypatch):
    gen, _ = _fake_generate()
    c = GeminiImageClient(api_key="k", out_dir=str(tmp_path))
    monkeypatch.setattr(c, "_generate", gen)
    a = c.generate_broll_image("scene one")
    b = c.generate_broll_image("scene two")
    assert a != b


def test_empty_response_raises_rather_than_writing_a_broken_file(tmp_path, monkeypatch):
    import pytest
    c = GeminiImageClient(api_key="k", out_dir=str(tmp_path))
    monkeypatch.setattr(c, "_generate", lambda *a, **k: b"")
    with pytest.raises(RuntimeError):
        c.generate_broll_image("x")
