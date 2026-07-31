"""Joining Flow clips into a part.

Flow returns 720x1280 @24fps, one 10s clip per generation. Reels wants 1080x1920 @30fps, and a
part is several clips spliced together. If each clip isn't normalised to one spec first, the join
stutters at every boundary — which is exactly the kind of thing a viewer reads as "cheap".
"""
import pytest
from modules.assemble import concat, add_furniture, build_part


def _capture():
    calls = []
    return calls, lambda args: calls.append(args)


def test_every_clip_is_normalised_to_one_spec_before_joining():
    calls, run = _capture()
    concat(["a.mp4", "b.mp4", "c.mp4"], "/tmp/out/x.mp4", run=run)

    chain = " ".join(calls[0])
    assert chain.count("scale=1080:1920") == 3      # each input, not just the first
    assert chain.count("fps=30") == 3
    assert "concat=n=3:v=1:a=1" in chain


def test_audio_is_resampled_so_the_clips_do_not_drift():
    calls, run = _capture()
    concat(["a.mp4", "b.mp4"], "/tmp/out/x.mp4", run=run)
    chain = " ".join(calls[0])
    assert chain.count("aresample=48000") == 2


def test_the_output_streams_before_it_finishes_downloading():
    calls, run = _capture()
    concat(["a.mp4"], "/tmp/out/x.mp4", run=run)
    assert "+faststart" in calls[0]


def test_joining_nothing_is_an_error_not_an_empty_video():
    with pytest.raises(ValueError):
        concat([], "/tmp/out/x.mp4", run=lambda a: None)


def test_the_end_card_holds_the_last_frame_rather_than_cutting_to_black(monkeypatch):
    monkeypatch.setattr("modules.assemble.probe_duration", lambda p: 30.0)
    calls, run = _capture()
    add_furniture("in.mp4", "out.mp4", part=1, outro_top="A", outro_bottom="B", run=run)

    vf = " ".join(calls[0])
    assert "tpad=stop_mode=clone" in vf            # freeze the final frame
    assert "black@0.72" in vf                      # darkened, not replaced
    assert "gte(t,30.0)" in vf                     # text only after the story ends


def test_the_part_badge_and_ai_label_are_burned_in(monkeypatch):
    monkeypatch.setattr("modules.assemble.probe_duration", lambda p: 10.0)
    calls, run = _capture()
    add_furniture("in.mp4", "out.mp4", part=3, outro_top="A", outro_bottom="B", run=run)

    vf = " ".join(calls[0])
    assert "PART 3" in vf
    assert "AI-Generated" in vf


def test_the_clips_own_audio_is_never_re_encoded(monkeypatch):
    """Flow bakes lip sync into the pixels; re-encoding the audio risks drifting off it."""
    monkeypatch.setattr("modules.assemble.probe_duration", lambda p: 10.0)
    calls, run = _capture()
    add_furniture("in.mp4", "out.mp4", part=1, outro_top="A", outro_bottom="B", run=run)
    assert "copy" in calls[0]
