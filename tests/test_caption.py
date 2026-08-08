from modules.caption import build_caption, CaptionConfig


SCRIPT = {
    "title": "कर्ज़", "hook": "क्या आपने कभी ऐसा देखा है?",
    "hashtags": ["#horror", "#story"],
}


def test_caption_has_the_hook_and_the_tags():
    c = build_caption(SCRIPT)
    assert "क्या आपने कभी ऐसा देखा है?" in c
    assert "#horror" in c


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
    assert "#horror" in c                # tagging stays regardless


def test_part_cta_only_appears_for_a_series():
    solo = build_caption(SCRIPT)
    assert "Part" not in solo

    part = build_caption(SCRIPT, part_number=1, total_parts=3)
    assert "अगला पार्ट" in part            # a series promises the next part
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
    c = build_caption({**SCRIPT, "hashtags": ["#horror", "#horror", "#suspense"]})
    assert c.count("#horror") == 1
    assert c.count("#suspense") == 1


def test_missing_fields_do_not_crash():
    build_caption({})                    # no title, no hook, no hashtags


def test_caption_stays_within_instagram_limit():
    long_script = {"title": "T", "hook": "क " * 1000, "hashtags": ["#a"]}
    c = build_caption(long_script)
    assert len(c) <= 2200                # Instagram caption cap
    assert "#a" in c                     # tags survive truncation of the body


def test_part_one_does_not_claim_a_later_part_is_already_posted():
    """Posting Part 1, Part 2 does not exist yet — 'Part 2 is on the profile' sends the viewer
    looking for something that isn't there."""
    c = build_caption({"title": "T"}, part_number=1, total_parts=3)
    assert "Part 2 प्रोफाइल पर" not in c
    assert "कल" in c                      # promise the next one instead


def test_a_later_part_points_back_at_the_one_that_is_already_up():
    """On Part 2 the useful pointer is Part 1 — that one really is on the profile, and sending
    viewers to it is what turns a single view into a session."""
    c = build_caption({"title": "T"}, part_number=2, total_parts=3)
    assert "Part 1 प्रोफाइल पर है" in c


def test_instagram_gets_at_most_five_hashtags():
    """Instagram caps hashtags at 5 (down from 30) and Meta recommends 3-5 relevant ones.
    Hashtags categorise now — they do not add reach — so extras are wasted at best."""
    script = {"title": "T", "hashtags": ["#a", "#b", "#c", "#d", "#e", "#f", "#g"]}
    c = build_caption(script)
    assert c.count("#") <= 5


def test_the_most_relevant_hashtags_are_the_ones_kept():
    """Truncation must drop from the end, so the script's first (most specific) tags survive."""
    script = {"title": "T", "hashtags": ["#hindikahani", "#crimestory", "#suspense",
                                         "#darkstories", "#kahani", "#dropme", "#alsodrop"]}
    c = build_caption(script)
    assert "#hindikahani" in c and "#crimestory" in c
    assert "#dropme" not in c and "#alsodrop" not in c


def test_shorts_is_a_youtube_tag_and_does_not_go_on_instagram():
    script = {"title": "T", "hashtags": ["#crime"]}
    assert "#Shorts" not in build_caption(script)
    # on YouTube it is what marks the upload as a Short, so it must still be there
    assert "#Shorts" in build_caption(script, platform="youtube")


def test_youtube_is_not_held_to_instagrams_five_tag_cap():
    script = {"title": "T", "hashtags": [f"#t{i}" for i in range(8)]}
    assert build_caption(script, platform="youtube").count("#") > 5


def test_the_last_part_does_not_promise_a_next_one():
    """A finale that says "so you don't miss the next part" sends people to a dead profile.

    Shipped that way on आखरी कॉल Part 3, together with a "comment PART4" ask for a Part 4 that
    was never coming.
    """
    from modules.caption import build_caption

    script = {"hook": "अंत", "hashtags": ["#a"]}
    finale = build_caption(script, part_number=3, total_parts=3)
    middle = build_caption(script, part_number=2, total_parts=3)

    assert "अगला पार्ट" not in finale, "the last part promised a next part"
    assert "रोज़ नई कहानी" in finale
    assert "अगला पार्ट कल रात" in middle, "a middle part should still promise the next one"
