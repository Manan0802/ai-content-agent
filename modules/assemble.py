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


def concat(clips: list[str], dest: str, width: int = 1080, height: int = 1920,
           fps: int = 30, run=_run) -> str:
    """Join clips, normalising size/fps/audio so they splice without drift.

    Flow hands back 720x1280 @24fps; Reels wants 1080x1920 @30. Re-encoding every clip to one
    spec first is what stops the join from stuttering at each boundary.
    """
    if not clips:
        raise ValueError("no clips to assemble")
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)

    args = ["ffmpeg", "-v", "error"]
    for c in clips:
        args += ["-i", c]

    parts, n = [], len(clips)
    for i in range(n):
        parts.append(
            f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},fps={fps},setsar=1[v{i}];"
            f"[{i}:a]aresample=48000,asetpts=N/SR/TB[a{i}];"
        )
    chain = "".join(parts) + "".join(f"[v{i}][a{i}]" for i in range(n))
    chain += f"concat=n={n}:v=1:a=1[vout][aout]"

    args += ["-filter_complex", chain, "-map", "[vout]", "-map", "[aout]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-y", dest]
    run(args)
    return dest


def add_furniture(src: str, dest: str, part: int, outro_top: str, outro_bottom: str,
                  outro_sec: float = 2.6, run=_run) -> str:
    """Burn the PART badge and AI label over the video, then hold the last frame as an end card.

    The end card sits over the darkened final frame rather than black — cutting to black reads as
    cheap and kills the rewatch loop.
    """
    dur = probe_duration(src)
    font = "/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc"
    fontarg = f":fontfile={font}" if os.path.exists(font) else ""

    vf = (
        # PART N badge, top left
        f"drawbox=x=40:y=60:w=190:h=64:color=0xC81414@0.85:t=fill,"
        f"drawtext=text='PART {part}':x=68:y=76:fontsize=36:fontcolor=white{fontarg},"
        # AI label, top right
        f"drawbox=x=w-300:y=60:w=260:h=52:color=black@0.55:t=fill,"
        f"drawtext=text='AI-Generated':x=w-282:y=74:fontsize=26:fontcolor=white{fontarg},"
        # end card: freeze the last frame, darken it, hold the text over it
        f"tpad=stop_mode=clone:stop_duration={outro_sec},"
        f"drawbox=enable='gte(t,{dur})':x=0:y=0:w=iw:h=ih:color=black@0.72:t=fill,"
        f"drawtext=enable='gte(t,{dur})':text='{outro_top}':"
        f"x=(w-text_w)/2:y=h/2-90:fontsize=74:fontcolor=white{fontarg},"
        f"drawtext=enable='gte(t,{dur})':text='{outro_bottom}':"
        f"x=(w-text_w)/2:y=h/2+20:fontsize=74:fontcolor=0xFF3B30{fontarg}"
    )
    run(["ffmpeg", "-v", "error", "-i", src, "-vf", vf,
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-c:a", "copy", "-movflags", "+faststart", "-y", dest])
    return dest


def build_part(clips: list[str], out_dir: str, part: int,
               outro_top: str, outro_bottom: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    joined = os.path.join(out_dir, "_joined.mp4")
    final = os.path.join(out_dir, "final.mp4")
    concat(clips, joined)
    add_furniture(joined, final, part, outro_top, outro_bottom)
    os.remove(joined)
    return final
