# -*- coding: utf-8 -*-
"""Take the generated clips of one video and produce the upload-ready part.

Order matters and each step exists because something shipped wrong without it:

1. **Whisper round-trip every clip.** Veo has twice spoken a different word from the one written
   (`पहचाण` -> "पैर पैन", `पाछै` -> "अच्छे"), and both times it was caught here rather than by
   listening once. Runs locally on mlx-whisper now — Groq's key is dead.
2. **Take the trim point from Whisper's own segment end**, not from `speech_end()`. Flow returns a
   full 10 seconds however short the line is, and `speech_end()`'s noise-floor method fails on
   continuous machine noise. Whisper already knows where the speech stopped, so use that and keep
   `speech_end()` as the fallback.
3. **Assemble** with `build_part` — normalise to 1080x1920/30fps, concat, PART badge, AI label,
   end card over the darkened last frame, audio faded and padded under it.
4. **Caption + meta**, then publish into `library/<niche>/<series>/part_NN/`.

    python3 tools/assemble_batch2.py <video_key>
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "content", "batch2"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from videos import VIDEOS                                    # noqa: E402
from modules.assemble import build_part, probe_duration, speech_end   # noqa: E402
from modules.caption import build_caption, CaptionConfig     # noqa: E402
from modules.library import publish                          # noqa: E402

CLIP_ROOT = "/tmp/aica_clips"
TAIL = 0.45          # the beat that stops a cut landing on the last syllable


def verify(clip: str, expected: str, lang: str) -> tuple[str, float, list]:
    """Transcribe the clip back: (heard, speech_end_seconds, words that look substituted)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from verify_lines import transcribe, speech_end as whisper_end, _matched
    code = "hi"      # Haryanvi has no Whisper code; hi transcribes it well enough to compare
    r = transcribe(clip, language=code)
    heard = r["text"].strip()
    suspect = [w for w in expected.split() if not _matched(w, heard.split())]
    return heard, whisper_end(r), suspect


def main() -> None:
    key = sys.argv[1]
    v = VIDEOS[key]
    root = os.path.join(CLIP_ROOT, key)
    clips, ends, report, flagged = [], [], [], []

    for i, shot in enumerate(v["shots"], 1):
        path = os.path.join(root, f"c{i}.mp4")
        if not os.path.exists(path):
            print(f"MISSING clip {i} — cannot assemble {key}")
            return
        heard, w_end, suspect = verify(path, shot["line"], v["lang"])
        dur = probe_duration(path)
        # Whisper's segment end is the better trim point WHEN it segments finely. On three of
        # v4's clips it returned one coarse segment spanning the whole 10s, which reads as "speech
        # runs to the very end" and trims nothing — hiding 3-4s of dead air per clip, which is
        # exactly the sluggishness the trimming exists to remove. When Whisper's end sits at the
        # clip's own duration it carries no information, so fall back to measuring the audio.
        if w_end and w_end < dur - 0.25:
            end = min(w_end + TAIL, dur)
        else:
            end = speech_end(path)
        clips.append(path)
        ends.append(round(end, 2))
        report.append({"clip": i, "written": shot["line"], "heard": heard,
                       "speech_end": round(w_end, 2), "trim_to": round(end, 2),
                       "raw": round(dur, 2), "suspect": suspect})
        if suspect:
            flagged.append((i, shot["line"], heard, suspect))
        print(f"[{i}] {round(dur,1)}s -> {round(end,2)}s{'  ⚠' if suspect else ''}")
        print(f"    written: {shot['line']}")
        print(f"    heard  : {heard}")
        if suspect:
            print(f"    ⚠ POSSIBLE MISREAD: {suspect}")

    # Veo has twice spoken a different word from the one written, and both times it was caught
    # here. Refuse to assemble on a suspected misread rather than bury it in meta.json.
    if flagged:
        print("\n" + "=" * 60)
        print(f"REFUSING TO ASSEMBLE {key} — {len(flagged)} clip(s) may have been misread:")
        for i, written, heard, sus in flagged:
            print(f"  clip {i}: {sus}")
            print(f"    written: {written}")
            print(f"    heard  : {heard}")
        print("Read each pair. If it is only Whisper's spelling, re-run with ALLOW_MISREAD=1.")
        print("=" * 60)
        if not os.environ.get("ALLOW_MISREAD"):
            return

    out_dir = os.path.join("outputs", f"batch2_{key}")
    final = build_part(clips, out_dir, v["part"], v["outro"][0], v["outro"][1], ends=ends)
    total = probe_duration(final)
    print(f"\nassembled {final} — {total:.2f}s")

    script = {"hook": v["hook"], "hashtags": v["hashtags"]}
    # the hook emoji is per-video: 😱 sells a horror short and undercuts a drama
    cfg = CaptionConfig(hook_emoji=v["emoji"])
    ig = build_caption(script, config=cfg, part_number=v["part"],
                       total_parts=v["total_parts"], platform="instagram")
    yt = build_caption(script, config=cfg, part_number=v["part"],
                       total_parts=v["total_parts"], platform="youtube")
    meta = {"series": v["title"], "part": v["part"], "total_parts": v["total_parts"],
            "language": v["lang"], "clips": len(clips), "duration_sec": round(total, 2),
            "resolution": "1080x1920", "fps": 30, "youtube_caption": yt,
            "lines": [f"{s['lock']}: {s['line']}" for s in v["shots"]],
            "verification": report}
    if not v["part"]:
        meta["standalone"] = True

    dest = publish(final, v["niche"], v["slug"], max(v["part"], 1), caption=ig, meta=meta)
    print(f"published -> {dest}")
    print(json.dumps({"duration": round(total, 2), "dir": dest}, ensure_ascii=False))


if __name__ == "__main__":
    main()
