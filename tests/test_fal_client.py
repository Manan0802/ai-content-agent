from integrations.fal_client import FalClient


def test_hero_image_calls_flux2(monkeypatch):
    captured = {}

    def fake_submit(model, arguments):
        captured["model"] = model
        captured["arguments"] = arguments
        return {"images": [{"url": "https://example.com/hero.png"}]}

    c = FalClient(api_key="x")
    monkeypatch.setattr(c, "_submit", fake_submit)
    url = c.generate_hero_image("a monk in a cursed fort", "https://example.com/ref.png")
    assert url == "https://example.com/hero.png"
    assert captured["model"] == FalClient.FLUX2_DEV
    assert captured["arguments"]["image_urls"] == ["https://example.com/ref.png"]


def test_broll_image_calls_flux_schnell(monkeypatch):
    def fake_submit(model, arguments):
        return {"images": [{"url": "https://example.com/broll.png"}]}

    c = FalClient(api_key="x")
    monkeypatch.setattr(c, "_submit", fake_submit)
    url = c.generate_broll_image("an old temple at night")
    assert url == "https://example.com/broll.png"
