"""The finished-video library, organised the way the channel is: domain -> series -> part.

`outputs/<job_id>/` stays the pipeline's scratch space. This is where a human looks.
"""
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
            caption: str = "", root: str = "library") -> str:
    """Copy a finished render into the library and drop the caption next to it."""
    dest = part_dir(niche, series_title, part, root=root)
    os.makedirs(dest, exist_ok=True)
    shutil.copy2(video_path, os.path.join(dest, "final.mp4"))
    if caption:
        with open(os.path.join(dest, "caption.txt"), "w", encoding="utf-8") as f:
            f.write(caption)
    return dest
