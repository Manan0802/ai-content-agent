"""Assemble Veo/Flow clips into a finished, upload-ready part.

Flow returns one 10s clip per generation, and the reference accounts work the same way — one
speaker per clip, conversations cut together afterwards. So the pipeline's job here is not to
render anything, it is to join real video clips and add the channel furniture:

- PART N badge (top left)
- AI-Generated label (top right)
- an end card over the darkened last frame, promising the next part

Everything is ffmpeg — the clips already have their own audio and lip sync baked in, so there is
nothing to time against and no HyperFrames render needed.
"""
import os
import subprocess

# This machine's ffmpeg is built without libfreetype, so `drawtext` does not exist. Overlays are
# rendered to transparent PNGs with Pillow instead — which also gives far better Devanagari
# shaping than drawtext would have.
_DEVANAGARI = "/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc"


def _font(size: int):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(_DEVANAGARI, size)
    except OSError:
        return ImageFont.load_default()


def render_badge(text: str, dest: str, bg: tuple, fg: tuple = (255, 255, 255, 255),
                 size: int = 38, pad: int = 22) -> str:
    """A small rounded label (PART N / AI-Generated) as a transparent PNG."""
    from PIL import Image, ImageDraw
    font = _font(size)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = probe.textbbox((0, 0), text, font=font)
    w, h = r - l + pad * 2, b - t + pad
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=12, fill=bg)
    d.text((pad - l, pad // 2 - t), text, font=font, fill=fg)
    img.save(dest)
    return dest


def render_end_card(top: str, bottom: str, dest: str, width: int = 1080,
                    height: int = 1920) -> str:
    """Full-frame end card: white line above, red line below, transparent elsewhere."""
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for text, y, colour, size in ((top, height // 2 - 110, (255, 255, 255, 255), 74),
                                  (bottom, height // 2 + 10, (255, 59, 48, 255), 78)):
        font = _font(size)
        l, t, r, b = d.textbbox((0, 0), text, font=font)
        d.text(((width - (r - l)) // 2 - l, y - t), text, font=font, fill=colour)
    img.save(dest)
    return dest


def probe_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def _run(args: list[str]) -> None:
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr[-600:]}")


def speech_end(path: str, tail: float = 0.45) -> float:
    """Seconds at which the spoken line finishes, plus a beat to breathe.

    Flow always returns a full 10s no matter how short the line is, so every clip carries about
    four seconds of nobody saying anything. Cutting there is the difference between the slack
    pacing of our earlier attempts and the fast cutting of the reference reels.

    `silencedetect` is no use here — a dhaba is never quiet, so the level never drops below any
    fixed threshold. Nor does a fixed margin above the noise floor: on the clip with loud dish
    clatter that kept every frame "voiced" and trimmed nothing at all.

    Reading against the clip's own floor and peak fixes that, because speech sits far above
    ambience in both. 60% of the way up is the level that holds: at the midpoint, one clip's
    dish clatter still read as speech and reported 9.20s against Whisper's 4.80s. Checked on
    four clips against Whisper's segment timings — 5.00/5.02, 5.70/5.86, 5.80/5.80, 4.75/4.80.
    """
    import wave
    import tempfile
    import numpy as np

    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav")
        _run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "1", "-ar", "16000", wav])
        with wave.open(wav) as w:
            sr = w.getframerate()
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)

    step = int(sr * 0.05)
    rms = np.array([np.sqrt((a[i:i + step] ** 2).mean() + 1e-9) for i in range(0, len(a) - step, step)])
    db = 20 * np.log10(rms / 32768 + 1e-9)
    floor, peak = np.percentile(db, 20), np.percentile(db, 98)
    voiced = np.where(db > floor + (peak - floor) * 0.6)[0]
    if not len(voiced):
        return probe_duration(path)
    return min((voiced[-1] + 1) * 0.05 + tail, probe_duration(path))


def concat(clips: list[str], dest: str, width: int = 1080, height: int = 1920,
           fps: int = 30, run=_run, ends: list[float] | None = None) -> str:
    """Join clips, normalising size/fps/audio so they splice without drift.

    Flow hands back 720x1280 @24fps; Reels wants 1080x1920 @30. Re-encoding every clip to one
    spec first is what stops the join from stuttering at each boundary.

    `ends` trims each clip to that many seconds — pass `speech_end()` values to drop Flow's dead
    tail. Leave it None to keep the clips whole.
    """
    if not clips:
        raise ValueError("no clips to assemble")
    if ends is not None and len(ends) != len(clips):
        raise ValueError("ends must line up with clips")
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)

    args = ["ffmpeg", "-v", "error"]
    for c in clips:
        args += ["-i", c]

    parts, n = [], len(clips)
    for i in range(n):
        vcut = f"trim=0:{ends[i]:.2f},setpts=PTS-STARTPTS," if ends else ""
        acut = f"atrim=0:{ends[i]:.2f}," if ends else ""
        parts.append(
            f"[{i}:v]{vcut}scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},fps={fps},setsar=1[v{i}];"
            f"[{i}:a]{acut}aresample=48000,asetpts=N/SR/TB[a{i}];"
        )
    chain = "".join(parts) + "".join(f"[v{i}][a{i}]" for i in range(n))
    chain += f"concat=n={n}:v=1:a=1[vout][aout]"

    args += ["-filter_complex", chain, "-map", "[vout]", "-map", "[aout]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-y", dest]
    run(args)
    return dest


def add_furniture(src: str, dest: str, part: int, outro_top: str, outro_bottom: str,
                  outro_sec: float = 2.6, run=_run, work_dir: str | None = None) -> str:
    """Overlay the PART badge and AI label, then hold the darkened last frame as an end card.

    The end card sits over the frozen final frame rather than black — cutting to black reads as
    cheap and kills the rewatch loop.
    """
    dur = probe_duration(src)
    work = work_dir or os.path.dirname(os.path.abspath(dest))
    os.makedirs(work, exist_ok=True)
    # part 0 means the video stands alone — a PART badge on a story that finishes would promise
    # a sequel that isn't coming.
    badge = render_badge(f"PART {part}" if part else " ",
                         os.path.join(work, "_badge.png"),
                         (200, 20, 20, 220) if part else (0, 0, 0, 0))
    label = render_badge("AI-Generated", os.path.join(work, "_label.png"), (0, 0, 0, 140), size=26)
    card = render_end_card(outro_top, outro_bottom, os.path.join(work, "_card.png"))

    # The frozen end card outlasts the audio, so without this the room tone stops dead the
    # instant the card appears. Fading it out reads as an ending; cutting it reads as a bug.
    afilter = (f"[0:a]afade=t=out:st={max(dur - 0.6, 0):.2f}:d=0.6,"
               f"apad=pad_dur={outro_sec}[aout]")

    chain = (
        # freeze the last frame for the end card, then darken only that stretch
        f"[0:v]tpad=stop_mode=clone:stop_duration={outro_sec}[v];"
        f"[v][1:v]overlay=40:60[v1];"
        f"[v1][2:v]overlay=W-w-40:62[v2];"
        f"[v2]drawbox=enable='gte(t,{dur})':x=0:y=0:w=iw:h=ih:color=black@0.72:t=fill[v3];"
        f"[v3][3:v]overlay=0:0:enable='gte(t,{dur})'[vout]"
    )
    run(["ffmpeg", "-v", "error", "-i", src, "-i", badge, "-i", label, "-i", card,
         "-filter_complex", chain + ";" + afilter, "-map", "[vout]", "-map", "[aout]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-y", dest])
    for f in (badge, label, card):
        os.remove(f)
    return dest


def build_part(clips: list[str], out_dir: str, part: int,
               outro_top: str, outro_bottom: str, trim: bool = True,
               ends: list[float] | None = None) -> str:
    """Pass `ends` to override the measured trim points.

    `speech_end` assumes ambience sits well below speech, which holds in a dhaba and fails on a
    moving motorcycle — the engine never drops, so nothing gets trimmed. When the caller already
    has better numbers (Whisper's segment timings, or a chosen length for a shot with no
    dialogue), they win.
    """
    os.makedirs(out_dir, exist_ok=True)
    joined = os.path.join(out_dir, "_joined.mp4")
    final = os.path.join(out_dir, "final.mp4")
    if ends is None and trim:
        ends = [speech_end(c) for c in clips]
    concat(clips, joined, ends=ends if trim else None)
    add_furniture(joined, final, part, outro_top, outro_bottom)
    os.remove(joined)
    return final
