"""Builds the review gallery from the contents of library/.

There is no separate list of videos to maintain — the library IS the list. Render a part and the
next build picks it up. Output is a plain static directory, deployable to Cloudflare Pages.
"""
import json
import os
import re
import shutil

from modules.preview import make_preview

_PART_RE = re.compile(r"^part_(\d+)$")


def scan_library(root: str = "library") -> list[dict]:
    items = []
    if not os.path.isdir(root):
        return items

    for niche in sorted(os.listdir(root)):
        niche_dir = os.path.join(root, niche)
        if not os.path.isdir(niche_dir):
            continue
        for series in sorted(os.listdir(niche_dir)):
            series_dir = os.path.join(niche_dir, series)
            if not os.path.isdir(series_dir):
                continue
            for part_name in sorted(os.listdir(series_dir)):
                m = _PART_RE.match(part_name)
                if not m:
                    continue
                part_dir = os.path.join(series_dir, part_name)
                master = os.path.join(part_dir, "final.mp4")
                if not os.path.exists(master):
                    continue          # rendered half-way, or a job that failed
                caption_path = os.path.join(part_dir, "caption.txt")
                caption = ""
                if os.path.exists(caption_path):
                    with open(caption_path, encoding="utf-8") as f:
                        caption = f.read()
                meta = {}
                meta_path = os.path.join(part_dir, "meta.json")
                if os.path.exists(meta_path):
                    with open(meta_path, encoding="utf-8") as f:
                        meta = json.load(f)
                items.append({
                    "meta": meta,
                    "id": f"{niche}/{series}/{part_name}",
                    "niche": niche,
                    "series": series,
                    "part": int(m.group(1)),
                    "master": master,
                    "caption": caption,
                })
    return items


def build_site(library_root: str = "library", out_dir: str = "web/public",
               preview=make_preview) -> dict:
    items = scan_library(library_root)
    entries = []

    for item in items:
        rel = f"previews/{item['niche']}/{item['series']}/part_{item['part']:02d}.mp4"
        dest = os.path.join(out_dir, rel)
        size = preview(item["master"], dest)
        entries.append({**item, "preview": rel, "preview_bytes": size})

    os.makedirs(out_dir, exist_ok=True)
    manifest = {"items": entries}
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # the page itself lives in the repo, not in generated output
    page = os.path.join("web", "index.html")
    if os.path.exists(page):
        shutil.copy2(page, os.path.join(out_dir, "index.html"))
    return manifest
