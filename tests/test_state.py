from orchestrator.state import new_state


def test_new_state_sets_meta_and_defaults():
    s = new_state(niche="horror", mode="semi_auto", language="hinglish",
                  format="short", hitl_checkpoints=["topic", "script"])
    assert s["niche"] == "horror"
    assert s["mode"] == "semi_auto"
    assert s["status"] == "idle"
    assert s["job_id"]
    assert s["created_at"]
    assert s["topic_candidates"] == []
    assert s["errors"] == []
    assert s["human_approved"] == {}
    assert s["hitl_checkpoints"] == ["topic", "script"]
