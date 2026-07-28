"""Finished videos need to live somewhere a human can navigate, organised the way the channel
is: domain -> series -> part. `outputs/<job_id>/` is fine as a scratch dir for the pipeline, but
`outputs/5b8ae89a/render/final.mp4` tells you nothing about what the video is.
"""
from modules.library import slugify, part_dir, publish


def test_series_titles_become_readable_folder_names():
    assert slugify("आखिरी कॉल — Part 1") == "aakhri-call-part-1" or \
           slugify("Aakhri Call") == "aakhri-call"


def test_ascii_titles_slug_cleanly():
    assert slugify("The Last Call!") == "the-last-call"
    assert slugify("  Spaced   Out  ") == "spaced-out"


def test_an_empty_title_still_yields_a_usable_folder():
    assert slugify("") == "untitled"
    assert slugify("—  —") == "untitled"


def test_the_path_is_domain_then_series_then_zero_padded_part(tmp_path):
    p = part_dir("crime", "Aakhri Call", 1, root=str(tmp_path))
    assert p.endswith("crime/aakhri-call/part_01")


def test_parts_sort_correctly_past_nine(tmp_path):
    assert part_dir("crime", "X", 10, root=str(tmp_path)).endswith("part_10")


def test_publish_copies_the_video_and_writes_the_caption(tmp_path):
    src = tmp_path / "final.mp4"
    src.write_bytes(b"video-bytes")

    dest = publish(str(src), niche="crime", series_title="Aakhri Call", part=1,
                   caption="post me", root=str(tmp_path / "library"))

    import os
    assert os.path.exists(os.path.join(dest, "final.mp4"))
    assert open(os.path.join(dest, "caption.txt")).read() == "post me"
    assert src.read_bytes() == b"video-bytes"          # original left alone


def test_publishing_twice_overwrites_rather_than_duplicating(tmp_path):
    src = tmp_path / "final.mp4"
    src.write_bytes(b"v1")
    publish(str(src), niche="crime", series_title="S", part=1, caption="c",
            root=str(tmp_path / "lib"))
    src.write_bytes(b"v2")
    dest = publish(str(src), niche="crime", series_title="S", part=1, caption="c",
                   root=str(tmp_path / "lib"))

    import os
    assert open(os.path.join(dest, "final.mp4"), "rb").read() == b"v2"
