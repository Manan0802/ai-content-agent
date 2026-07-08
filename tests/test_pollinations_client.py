from integrations.pollinations_client import PollinationsClient


def test_broll_url_encodes_prompt_and_params():
    c = PollinationsClient(width=1080, height=1920)
    url = c.generate_broll_image("an old temple at night")
    assert url.startswith("https://image.pollinations.ai/prompt/")
    assert "an%20old%20temple%20at%20night" in url
    assert "width=1080" in url
    assert "height=1920" in url
    assert "model=flux" in url
    assert "nologo=true" in url
    assert "seed=" in url


def test_same_prompt_is_deterministic():
    c = PollinationsClient()
    assert c.generate_broll_image("dark fort") == c.generate_broll_image("dark fort")


def test_different_prompts_differ():
    c = PollinationsClient()
    assert c.generate_broll_image("dark fort") != c.generate_broll_image("bright temple")


def test_hero_ignores_reference_but_returns_url():
    c = PollinationsClient()
    url = c.generate_hero_image("a monk", "https://x/ref.png")
    assert url.startswith("https://image.pollinations.ai/prompt/")
    assert "a%20monk" in url
