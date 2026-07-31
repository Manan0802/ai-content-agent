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


def test_the_badges_are_rendered_as_images_not_drawtext(monkeypatch, tmp_path):
    """This machine's ffmpeg is built without libfreetype, so `drawtext` does not exist —
    caught by running the assembler on a real Flow clip, not by the unit tests."""
    monkeypatch.setattr("modules.assemble.probe_duration", lambda p: 10.0)
    calls, run = _capture()
    add_furniture("in.mp4", str(tmp_path / "out.mp4"), part=3, outro_top="A", outro_bottom="B",
                  run=run, work_dir=str(tmp_path))

    args = calls[0]
    assert "drawtext" not in " ".join(args)
    assert args.count("-i") == 4                 # video + badge + label + end card
    assert " ".join(args).count("overlay") == 3


def test_the_badge_image_actually_contains_the_part_number(tmp_path):
    from modules.assemble import render_badge
    p = render_badge("PART 3", str(tmp_path / "b.png"), (200, 20, 20, 220))
    from PIL import Image
    img = Image.open(p)
    assert img.mode == "RGBA" and img.width > 60      # real label, not an empty tile


def test_the_end_card_is_a_full_frame_transparent_overlay(tmp_path):
    from modules.assemble import render_end_card
    from PIL import Image
    p = render_end_card("काळू ने क्या छुपाया था?", "PART 2", str(tmp_path / "c.png"))
    img = Image.open(p)
    assert img.size == (1080, 1920)
    assert img.getpixel((5, 5))[3] == 0               # corners stay transparent


def test_the_audio_is_never_shifted_against_the_picture(monkeypatch):
    """Flow bakes lip sync into the pixels, so nothing here may move the audio's start.

    This used to insist on `-c:a copy`, which was a proxy for the same thing. The end card
    outlasts the audio, and without a fade the room tone stopped dead the instant it appeared —
    fixing that needs a filter, and a filter needs a re-encode. Measured before allowing it:
    cross-correlating the first four seconds before and after `add_furniture` gives a **0 sample**
    offset, because ffmpeg carries AAC encoder delay in the MP4 edit list.

    So the rule is the real one — fade and pad at the END are fine, anything that re-times the
    start is not.
    """
    monkeypatch.setattr("modules.assemble.probe_duration", lambda p: 10.0)
    calls, run = _capture()
    add_furniture("in.mp4", "out.mp4", part=1, outro_top="A", outro_bottom="B", run=run)
    chain = calls[0][calls[0].index("-filter_complex") + 1]
    for shifter in ("adelay", "atrim", "asetpts", "atempo"):
        assert shifter not in chain, f"{shifter} would move the audio off the lip sync"
