# -*- coding: utf-8 -*-
"""The check that turns "probably fine" into "ready", run against the assembled cut.

Verifying the source clips is not enough — the concat can drift, the trim points can be wrong,
and the end card can land on the wrong frame. So this re-checks the FINAL file:

1. container/stream facts — 1080x1920, 30fps, an audio track that matches the video's length
2. `ffmpeg -f null -` for decode errors
3. **picture and sound together** — slice the final at every segment boundary, transcribe that
   slice, and confirm it carries the line that shot was written for. This is what catches a
   mis-ordered or mis-trimmed cut, which listening once would not.
4. a contact sheet, one frame per shot plus the end card, so every card can be read against its
   own line — the habit that caught the torch, the empty room and the grinning dog

    python3 tools/verify_final.py <video_key>
"""
import difflib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "content", "batch2"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from videos import VIDEOS                     # noqa: E402
from modules.library import part_dir          # noqa: E402
from verify_lines import transcribe, _matched, _skeleton  # noqa: E402


def _sk(text: str) -> str:
    return "".join(_skeleton(w) for w in text.split())


def _probe(path: str, stream: str, field: str) -> str:
    return subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", stream,
         "-show_entries", f"stream={field}", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout.strip().rstrip(",")


def main() -> None:
    key = sys.argv[1]
    v = VIDEOS[key]
    d = part_dir(v["niche"], v["slug"], max(v["part"], 1))
    final = os.path.join(d, "final.mp4")
    meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
    ends = [c["trim_to"] for c in meta["verification"]]

    print(f"=== {key}: {v['title']} -> {d}")
    ok = True

    w, h = _probe(final, "v:0", "width"), _probe(final, "v:0", "height")
    fps = _probe(final, "v:0", "r_frame_rate")
    print(f"[format] {w}x{h} @ {fps}")
    if (w, h) != ("1080", "1920"):
        print("  !! not 1080x1920"); ok = False

    vd = float(_probe(final, "v:0", "duration"))
    ad_raw = _probe(final, "a:0", "duration")
    if not ad_raw:
        print("[audio ] no audio track — correct only for a music-mode video"); ad = None
    else:
        ad = float(ad_raw)
        print(f"[audio ] video {vd:.2f}s  audio {ad:.2f}s  diff {abs(vd - ad):.2f}s")
        if abs(vd - ad) > 0.5:
            print("  !! audio and video lengths disagree"); ok = False

    err = subprocess.run(["ffmpeg", "-v", "error", "-i", final, "-f", "null", "-"],
                         capture_output=True, text=True).stderr.strip()
    print(f"[decode] {'clean' if not err else err[:200]}")
    if err:
        ok = False

    print("[sync  ] slicing the final at each boundary:")
    t = 0.0
    for i, (end, shot) in enumerate(zip(ends, v["shots"]), 1):
        seg = f"/tmp/_vf_{key}_{i}.mp4"
        # Re-encode rather than stream-copy. `-c copy` seeks to the nearest keyframe and drops
        # the audio before it, which silently ate "मम्मी जी" off the front of a segment and
        # reported a mismatch that did not exist. A verification step that can invent its own
        # failures is worse than none — and the same artifact could just as easily hide a real one.
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-t", f"{end:.2f}",
                        "-i", final, "-c:a", "aac", "-c:v", "libx264", "-preset", "ultrafast",
                        seg], check=True)
        heard = transcribe(seg)["text"].strip()
        # What this step is actually for is ORDER: is the right line in the right place, and does
        # the character on screen match the voice? Word-perfect matching belongs on the source
        # clip, where Whisper sees the whole 10s. On a short slice it intermittently drops a
        # leading phrase — "मम्मी जी" vanished from a 6.61s window and came back in an 8s one —
        # so demanding every word here invents failures. Instead, score the slice against EVERY
        # line in the video: it must resemble its own line more than any other. A swapped,
        # duplicated or mis-trimmed segment fails that; a dropped opening word does not.
        best = max(range(len(v["shots"])),
                   key=lambda k: difflib.SequenceMatcher(
                       None, _sk(v["shots"][k]["line"]), _sk(heard)).ratio())
        mine = difflib.SequenceMatcher(None, _sk(shot["line"]), _sk(heard)).ratio()
        dropped = [x for x in shot["line"].split() if not _matched(x, heard.split())]
        print(f"  [{i}] {t:5.2f}-{t + end:5.2f}s  {shot['lock']}")
        print(f"      written: {shot['line']}")
        print(f"      heard  : {heard}  (match {mine:.2f})")
        if best != i - 1:
            print(f"      !! WRONG LINE HERE — resembles shot {best + 1} more"); ok = False
        elif dropped:
            print(f"      note: Whisper did not return {dropped} on this short slice "
                  f"(already verified on the source clip)")
        t += end

    from PIL import Image
    mids, c = [], 0.0
    for e in ends:
        mids.append(c + e / 2); c += e
    mids.append(c + 1.3)
    ims = []
    for i, m in enumerate(mids):
        p = f"/tmp/_vf_{key}_f{i}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{m:.2f}", "-i", final,
                        "-frames:v", "1", p], check=True)
        ims.append(Image.open(p))
    sw, sh = ims[0].size[0] // 5, ims[0].size[1] // 5
    sheet = Image.new("RGB", (sw * len(ims), sh), (0, 0, 0))
    for i, im in enumerate(ims):
        sheet.paste(im.resize((sw, sh)), (i * sw, 0))
    out = f"/tmp/{key}_sheet.jpg"
    sheet.save(out, quality=88)
    print(f"[frames] {out} — read every card against its line above")

    print(f"\n{'VERIFIED — upload ready' if ok else 'NOT READY — see the !! lines'}")


if __name__ == "__main__":
    main()
