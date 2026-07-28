"""The finished-video library, organised the way the channel is: domain -> series -> part.

`outputs/<job_id>/` stays the pipeline's scratch space. This is where a human looks.
"""
import json
import os
import re
import shutil
import unicodedata

_TRANSLIT = {
    "आखिरी": "aakhri", "कॉल": "call", "कहानी": "kahani", "रात": "raat",
    "खून": "khoon", "पुलिस": "police", "गाँव": "gaon",
}


def slugify(title: str) -> str:
    text = (title or "").strip()
    for deva, roman in _TRANSLIT.items():
        text = text.replace(deva, roman)
    # drop anything that isn't a word character; em-dashes and punctuation are not folder names
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text.strip()).strip("-").lower()
    return text or "untitled"


def part_dir(niche: str, series_title: str, part: int, root: str = "library") -> str:
    return os.path.join(root, slugify(niche), slugify(series_title), f"part_{part:02d}")


def publish(video_path: str, niche: str, series_title: str, part: int,
            caption: str = "", root: str = "library", meta: dict | None = None) -> str:
    """Copy a finished render into the library, with its caption and technical facts beside it.

    `meta` is written here rather than re-derived later because the pipeline is the only thing
    that knows the card count, format profile and measured sync gaps.
    """
    dest = part_dir(niche, series_title, part, root=root)
    os.makedirs(dest, exist_ok=True)
    final = os.path.join(dest, "final.mp4")
    # re-publishing an already-published part (e.g. to attach meta.json) points at itself
    if os.path.abspath(video_path) != os.path.abspath(final):
        shutil.copy2(video_path, final)
    if caption:
        with open(os.path.join(dest, "caption.txt"), "w", encoding="utf-8") as f:
            f.write(caption)
    if meta:
        with open(os.path.join(dest, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
    return dest
