from integrations.pollinations_client import PollinationsClient


def _client(**kw):
    # warm=False keeps URL-construction tests network-free
    kw.setdefault("warm", False)
    return PollinationsClient(**kw)


def test_broll_url_encodes_prompt_and_params():
    c = _client(width=1080, height=1920)
    url = c.generate_broll_image("an old temple at night")
    assert url.startswith("https://image.pollinations.ai/prompt/")
    assert "an%20old%20temple%20at%20night" in url
    assert "width=1080" in url
    assert "height=1920" in url
    assert "model=flux" in url
    assert "nologo=true" in url
    assert "seed=" in url


def test_same_prompt_is_deterministic():
    c = _client()
    assert c.generate_broll_image("dark fort") == c.generate_broll_image("dark fort")


def test_different_prompts_differ():
    c = _client()
    assert c.generate_broll_image("dark fort") != c.generate_broll_image("bright temple")


def test_hero_ignores_reference_but_returns_url():
    c = _client()
    url = c.generate_hero_image("a monk", "https://x/ref.png")
    assert url.startswith("https://image.pollinations.ai/prompt/")
    assert "a%20monk" in url


def test_warm_retries_on_failure_then_succeeds():
    calls = {"n": 0}

    def flaky_fetch(url, timeout=90):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("HTTP 429")
        return None

    c = PollinationsClient(warm=True, fetch=flaky_fetch, sleeper=lambda s: None,
                           max_retries=5, pace_sec=0)
    url = c.generate_broll_image("dark fort")
    assert url.startswith("https://image.pollinations.ai/prompt/")
    assert calls["n"] == 3  # failed twice, succeeded on the third


def test_warm_gives_up_quietly_after_max_retries():
    def always_fails(url, timeout=90):
        raise RuntimeError("HTTP 429")

    c = PollinationsClient(warm=True, fetch=always_fails, sleeper=lambda s: None,
                           max_retries=3, pace_sec=0)
    # should not raise — render still has the URL as a fallback
    url = c.generate_broll_image("dark fort")
    assert url.startswith("https://image.pollinations.ai/prompt/")
