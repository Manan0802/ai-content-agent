from modules.caption import build_caption, CaptionConfig


SCRIPT = {
    "title": "कर्ज़", "hook": "क्या आपने कभी ऐसा देखा है?",
    "hashtags": ["#horror", "#story"],
}


def test_caption_has_hook_and_shorts_tag():
    c = build_caption(SCRIPT)
    assert "क्या आपने कभी ऐसा देखा है?" in c
    assert "#Shorts" in c


def test_engagement_ctas_are_present_by_default():
    c = build_caption(SCRIPT)
    # the measured winner (technoyash_food, 72.7K comments > 59K likes) stacked all three asks
    assert "Follow" in c
    assert "3" in c                      # share with 3 friends
    assert "Comment" in c or "कमेंट" in c


def test_ctas_can_be_switched_off():
    c = build_caption(SCRIPT, CaptionConfig(follow_cta=False, share_cta=False,
                                            comment_cta=False))
    assert "Follow" not in c
    assert "#Shorts" in c                # tagging stays regardless


def test_part_cta_only_appears_for_a_series():
    solo = build_caption(SCRIPT)
    assert "Part" not in solo

    part = build_caption(SCRIPT, part_number=1, total_parts=3)
    assert "Part 2" in part               # points at the NEXT part
    assert "Part 4" not in build_caption(SCRIPT, part_number=3, total_parts=3)


def test_last_part_asks_to_follow_for_the_next_series():
    c = build_caption(SCRIPT, part_number=3, total_parts=3)
    assert "Part 4" not in c
    assert "Follow" in c


def test_youtube_link_included_when_given():
    c = build_caption(SCRIPT, youtube_url="https://youtu.be/abc")
    assert "https://youtu.be/abc" in c
    assert "https://youtu.be/abc" not in build_caption(SCRIPT)


def test_hashtags_from_script_are_kept_and_deduped():
    c = build_caption({**SCRIPT, "hashtags": ["#horror", "#horror", "#Shorts"]})
    assert c.count("#horror") == 1
    assert c.count("#Shorts") == 1


def test_missing_fields_do_not_crash():
    c = build_caption({})
    assert "#Shorts" in c


def test_caption_stays_within_instagram_limit():
    long_script = {"title": "T", "hook": "क " * 1000, "hashtags": ["#a"]}
    c = build_caption(long_script)
    assert len(c) <= 2200                # Instagram caption cap
    assert "#Shorts" in c                # tags survive truncation
