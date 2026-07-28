"""Cloudflare Pages caps a single static asset at 25 MiB. A finished 36s Short is ~30 MB, so the
master cannot be served from the gallery — and it shouldn't be: the master is what gets uploaded
to Instagram/YouTube, and re-encoding it for a review page would be throwing away quality for no
reason. The gallery gets a small preview instead.
"""
import os
import pytest
from modules.preview import PAGES_ASSET_LIMIT_BYTES, preview_args, make_preview


def test_the_limit_matches_what_cloudflare_pages_actually_enforces():
    assert PAGES_ASSET_LIMIT_BYTES == 25 * 1024 * 1024


def test_the_preview_is_downscaled_and_streamable():
    args = preview_args("in.mp4", "out.mp4")
    assert "720:1280" in " ".join(args)          # half of 1080x1920, still sharp on a phone
    assert "+faststart" in args                  # so it plays before the whole file arrives
    assert args[0] == "ffmpeg"
    assert args[-1] == "out.mp4"


def test_the_master_is_never_the_output():
    args = preview_args("master.mp4", "preview.mp4")
    assert args.count("master.mp4") == 1         # read once, as input
    assert args[-1] != "master.mp4"


def test_make_preview_rejects_a_result_that_pages_would_refuse(tmp_path):
    """If a future longer video encodes above the cap, fail loudly here rather than at deploy."""
    src = tmp_path / "in.mp4"
    src.write_bytes(b"x")
    out = tmp_path / "out.mp4"

    def fake_run(args):
        out.write_bytes(b"y" * (PAGES_ASSET_LIMIT_BYTES + 1))

    with pytest.raises(ValueError, match="25 MiB"):
        make_preview(str(src), str(out), run=fake_run)


def test_make_preview_returns_the_size_it_produced(tmp_path):
    src = tmp_path / "in.mp4"
    src.write_bytes(b"x")
    out = tmp_path / "out.mp4"

    size = make_preview(str(src), str(out), run=lambda a: out.write_bytes(b"y" * 1234))
    assert size == 1234
    assert os.path.exists(out)
