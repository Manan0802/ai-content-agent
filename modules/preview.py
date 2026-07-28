"""Small web-playable copy of a finished video, for the review gallery.

The master render stays untouched — that is what gets uploaded to Instagram and YouTube, and
re-encoding it would cost quality for nothing. This is only so the gallery can be a static
Cloudflare Pages site with no object storage behind it (and therefore no card on file).

Measured: a 36s 1080x1920 master at 29.8 MB encodes to 1.7 MB in ~4.5s.
"""
import os
import subprocess

PAGES_ASSET_LIMIT_BYTES = 25 * 1024 * 1024      # Cloudflare Pages: 25 MiB per static asset


def preview_args(src: str, dest: str) -> list[str]:
    return [
        "ffmpeg", "-v", "error", "-i", src,
        "-c:v", "libx264", "-crf", "28", "-preset", "medium",
        "-vf", "scale=720:1280",
        "-movflags", "+faststart",               # starts playing before the file finishes loading
        "-y", dest,
    ]


def _run(args: list[str]) -> None:
    subprocess.run(args, check=True, capture_output=True)


def make_preview(src: str, dest: str, run=_run) -> int:
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    run(preview_args(src, dest))
    size = os.path.getsize(dest)
    if size > PAGES_ASSET_LIMIT_BYTES:
        raise ValueError(
            f"preview is {size / 1048576:.1f} MB — Cloudflare Pages refuses assets over 25 MiB"
        )
    return size
