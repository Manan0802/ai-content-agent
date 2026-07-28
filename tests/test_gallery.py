"""The gallery is built from whatever is in library/ — no separate list to keep in sync.
Adding a part means rendering it; the next build picks it up.
"""
import json
import os
from modules.gallery import scan_library, build_site


def _make_part(root, niche, series, part, caption="cap"):
    d = os.path.join(root, niche, series, f"part_{part:02d}")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "final.mp4"), "wb").write(b"video")
    if caption:
        open(os.path.join(d, "caption.txt"), "w").write(caption)
    return d


def test_scan_finds_every_part_under_every_series(tmp_path):
    _make_part(str(tmp_path), "crime", "aakhri-call", 1)
    _make_part(str(tmp_path), "crime", "aakhri-call", 2)
    _make_part(str(tmp_path), "horror", "station", 1)

    items = scan_library(str(tmp_path))
    assert len(items) == 3
    assert {i["niche"] for i in items} == {"crime", "horror"}


def test_items_carry_the_caption_and_a_stable_id(tmp_path):
    _make_part(str(tmp_path), "crime", "aakhri-call", 1, caption="post this")
    item = scan_library(str(tmp_path))[0]

    assert item["caption"] == "post this"
    assert item["id"] == "crime/aakhri-call/part_01"     # stable across rebuilds


def test_parts_come_back_in_order(tmp_path):
    for p in (3, 1, 2):
        _make_part(str(tmp_path), "crime", "s", p)
    assert [i["part"] for i in scan_library(str(tmp_path))] == [1, 2, 3]


def test_a_directory_without_a_render_is_skipped(tmp_path):
    os.makedirs(os.path.join(str(tmp_path), "crime", "half-done", "part_01"))
    assert scan_library(str(tmp_path)) == []


def test_a_missing_library_is_empty_not_an_error(tmp_path):
    assert scan_library(str(tmp_path / "nope")) == []


def test_build_writes_a_manifest_and_a_preview_per_item(tmp_path):
    lib = tmp_path / "library"
    _make_part(str(lib), "crime", "aakhri-call", 1)
    out = tmp_path / "site"

    made = []

    def fake_preview(src, dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").write(b"small")
        made.append(dest)
        return 5

    build_site(str(lib), str(out), preview=fake_preview)

    manifest = json.load(open(out / "manifest.json"))
    assert len(manifest["items"]) == 1
    entry = manifest["items"][0]
    assert entry["preview"] == "previews/crime/aakhri-call/part_01.mp4"
    assert os.path.exists(out / entry["preview"])
    assert len(made) == 1


def test_the_manifest_records_the_master_path_so_it_can_be_found_locally(tmp_path):
    lib = tmp_path / "library"
    d = _make_part(str(lib), "crime", "s", 1)
    out = tmp_path / "site"
    build_site(str(lib), str(out),
               preview=lambda s, dst: (os.makedirs(os.path.dirname(dst), exist_ok=True),
                                       open(dst, "wb").write(b"x"), 1)[-1])

    entry = json.load(open(out / "manifest.json"))["items"][0]
    assert entry["master"].endswith("part_01/final.mp4")


def test_the_manifest_carries_the_technical_facts_when_present(tmp_path):
    import json
    lib = tmp_path / "library"
    d = _make_part(str(lib), "crime", "s", 1)
    open(os.path.join(d, "meta.json"), "w").write(
        json.dumps({"duration_sec": 38.6, "cards": 11, "format": "serial_75s"}))
    out = tmp_path / "site"
    build_site(str(lib), str(out),
               preview=lambda s, dst: (os.makedirs(os.path.dirname(dst), exist_ok=True),
                                       open(dst, "wb").write(b"x"), 1)[-1])

    entry = json.load(open(out / "manifest.json"))["items"][0]
    assert entry["meta"]["cards"] == 11
