import os
from orchestrator.state import ContentState
from modules.formats import get_format
from modules.camera import move_for


def text_mode_for(format_profile: str) -> str:
    """Whether dialogue is burned on screen, and how.

    Measured from the reference reels: the two biggest performers (98K and 32K likes) are
    narrated and burn NO dialogue at all — the voice carries it and a caption over it reads as
    amateur. Music-mode reels have no voice, so the text is the only channel and must stay.
    """
    try:
        return "none" if get_format(format_profile).audio_mode == "narrated" else "banner"
    except (ValueError, AttributeError):
        return "banner"      # unknown format: a caption we didn't need beats a silent video

_HEAD = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={width}, height={height}" />
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      body {{ margin: 0; background: #000; color: #fff; font-family: Inter, system-ui, sans-serif; }}
      #root {{ position: relative; width: {width}px; height: {height}px; overflow: hidden; }}
      .clip {{ position: absolute; inset: 0; }}
      .clip img {{ width: 100%; height: 100%; object-fit: cover; }}
      .caption {{ position: absolute; left: 5%; right: 5%; bottom: 8%; font-size: 48px;
                  text-align: center; text-shadow: 0 2px 8px rgba(0,0,0,.8); }}
      .disclosure-text {{ font-size: 40px; text-align: center; padding: 0 8%; }}
      .ai-label {{ inset: auto; top: 3%; right: 4%; bottom: auto; left: auto; font-size: 22px;
                   color: #fff; background: rgba(0,0,0,.55); padding: 6px 14px; border-radius: 8px;
                   z-index: 9999; }}
      /* on-screen dialogue: big Devanagari at the TOP of frame, matching the reference accounts */
      .dialogue {{ position: absolute; top: 7%; left: 4%; right: 4%; font-size: 70px;
                   font-weight: 900; line-height: 1.2; text-align: center; color: #fff;
                   -webkit-text-stroke: 4px #000; paint-order: stroke fill;
                   text-shadow: 0 6px 22px rgba(0,0,0,.95), 0 0 40px rgba(0,0,0,.7);
                   letter-spacing: -0.5px; z-index: 50; }}
      /* dark scrim behind the text so it stays readable on any image */
      .scrim {{ position: absolute; top: 0; left: 0; right: 0; height: 34%;
                background: linear-gradient(180deg, rgba(0,0,0,.75) 0%, rgba(0,0,0,0) 100%);
                z-index: 40; }}
      /* comic speech bubble, pointing at whoever is talking — what story_hub_life uses */
      .bubble {{ position: absolute; top: 9%; left: 8%; right: 8%; background: #fff;
                 color: #14161a; font-size: 46px; font-weight: 700; line-height: 1.3;
                 text-align: center; padding: 26px 30px; border-radius: 34px;
                 box-shadow: 0 10px 40px rgba(0,0,0,.55); z-index: 50; }}
      .bubble::after {{ content: ""; position: absolute; bottom: -26px; left: 16%;
                        border: 16px solid transparent; border-top: 28px solid #fff;
                        border-right-width: 26px; }}
      .bubble .hl {{ color: #c02020; -webkit-text-stroke: 0; }}
      /* one coloured word per card — where the eye should land in the ~2.5s it is up */
      .hl {{ color: #ff3b30; -webkit-text-stroke: 4px #000; }}
      .speaker {{ display: block; font-size: 30px; font-weight: 700; color: #ffd54a;
                  -webkit-text-stroke: 2px #000; margin-bottom: 10px; }}
      /* end card: the viewer who reached this point is the one most likely to follow */
      .outro {{ display: flex; align-items: center; justify-content: center; z-index: 60; }}
      /* the last frame stays under the end card — cutting to black kills the rewatch loop */
      .outro img {{ position: absolute; inset: 0; filter: brightness(0.28) saturate(0.7); }}
      .outro-text {{ font-size: 84px; font-weight: 900; text-align: center; color: #fff;
                     padding: 0 8%; line-height: 1.25; -webkit-text-stroke: 4px #000;
                     paint-order: stroke fill; }}
      .outro-text em {{ display: block; font-style: normal; color: #ff3b30; margin-top: 24px; }}
      .part-badge {{ inset: auto; top: 3%; left: 4%; bottom: auto; right: auto; font-size: 30px;
                     font-weight: 800; color: #fff; background: rgba(200,20,20,.85);
                     padding: 8px 18px; border-radius: 8px; z-index: 9999;
                     -webkit-text-stroke: 1px #000; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="{comp_id}" data-start="0" data-width="{width}" data-height="{height}" data-duration="{duration}">
      <div id="ai-label" class="clip ai-label" data-start="{label_start}" data-duration="{label_duration}" data-track-index="20">AI-Generated</div>
"""

_TAIL = """    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
{tweens}      window.__timelines["{comp_id}"] = tl;
    </script>
  </body>
</html>
"""


def composition_writer_node(state: ContentState, project_dir: str,
                            width: int = 1080, height: int = 1920,
                            disclosure_duration_sec: float = 3.0,
                            bgm_volume: float = 0.25,
                            text_mode: str | None = None) -> ContentState:
    try:
        mode = text_mode or text_mode_for(state.get("format_profile", ""))
        segments = state["script"]["segments"]
        visuals = {v["scene_number"]: v for v in state.get("visual_assets", [])}
        audio_assets = {a["scene_number"]: a for a in state.get("audio_assets", [])}
        disclosure_audio = state.get("disclosure_audio_path", "")

        clips, media_tags, tweens, cursor = [], [], [], 0.0

        if disclosure_audio:
            rel = os.path.relpath(disclosure_audio, project_dir)
            clips.append(
                f'      <section id="disclosure-intro" class="clip" data-start="{cursor}" '
                f'data-duration="{disclosure_duration_sec}" data-track-index="1">\n'
                f'        <p class="disclosure-text">This video uses AI-generated voice and visuals.</p>\n'
                f'      </section>'
            )
            media_tags.append(
                f'      <audio id="disclosure-audio" data-start="{cursor}" '
                f'data-duration="{disclosure_duration_sec}" data-track-index="10" src="{rel}"></audio>'
            )
            cursor += disclosure_duration_sec
        label_start = cursor

        # speaker id -> display name, so we can label lines when there is more than one character
        chars = state.get("script", {}).get("characters", []) or []
        names = {c.get("id"): c.get("name", "") for c in chars}
        show_speaker = len(chars) > 1

        for seg in segments:
            dur = float(seg["duration_sec"])
            image = visuals.get(seg["scene_number"], {}).get("image_url", "")
            # v2 scripts carry `dialogue` (+ speaker); Phase-1 ones carried `voiceover_text`
            text = seg.get("dialogue") or seg.get("voiceover_text", "")
            hl = seg.get("highlight", "")
            if hl and hl in text:
                text = text.replace(hl, f'<span class="hl">{hl}</span>', 1)
            speaker_name = names.get(seg.get("speaker"), "") if show_speaker else ""
            scene_id = f"scene-{seg['scene_number']}"
            speaker_html = (
                f'<span class="speaker">{speaker_name}</span>' if speaker_name else ""
            )
            if mode == "none":
                caption_html = ""
            elif mode == "bubble":
                caption_html = f'        <p class="bubble">{text}</p>\n'
            else:
                caption_html = (f'        <div class="scrim"></div>\n'
                                f'        <p class="dialogue">{speaker_html}{text}</p>\n')
            clips.append(
                f'      <section id="{scene_id}" class="clip" data-start="{cursor}" data-duration="{dur}" '
                f'data-track-index="1">\n'
                f'        <img src="{image}" crossorigin="anonymous" />\n'
                f'{caption_html}'
                f'      </section>'
            )
            sel = ".bubble" if mode == "bubble" else ".dialogue"
            # motion: slow push-in on the image + dialogue fading up.
            # Also required for correctness — an empty timeline never advances under seek and
            # `hyperframes check` fails the whole run with `sweep_static`.
            # a different move per scene — twelve identical zooms read as a slideshow
            frm, to = move_for(seg["scene_number"])
            tweens.append(
                f'      tl.fromTo("#{scene_id} img", '
                f'{{ scale: {frm["scale"]}, x: {frm.get("x", 0)}, y: {frm.get("y", 0)} }}, '
                f'{{ scale: {to["scale"]}, x: {to.get("x", 0)}, y: {to.get("y", 0)}, '
                f'duration: {dur}, ease: "none" }}, {cursor});\n'
            )
            tweens.append(
                f'      tl.fromTo("#{scene_id} {sel}", {{ opacity: 0, y: 30 }}, '
                f'{{ opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }}, {cursor});\n'
            )
            # crossfade in/out so scenes flow instead of hard-cutting
            if seg is not segments[0]:
                tweens.append(
                    f'      tl.fromTo("#{scene_id}", {{ opacity: 0 }}, '
                    f'{{ opacity: 1, duration: 0.35, ease: "power1.inOut" }}, {cursor});\n'
                )
            tweens.append(
                f'      tl.to("#{scene_id} {sel}", '
                f'{{ opacity: 0, duration: 0.25 }}, {round(cursor + dur - 0.25, 2)});\n'
            )
            # hard kill on the clip boundary — a seek that lands past the fade would otherwise
            # leave the previous scene's text visible (`gsap_exit_missing_hard_kill`)
            tweens.append(
                f'      tl.set("#{scene_id} {sel}", '
                f'{{ opacity: 0 }}, {round(cursor + dur, 2)});\n'
            )

            audio_path = audio_assets.get(seg["scene_number"], {}).get("audio_path", "")
            if audio_path:
                rel = os.path.relpath(audio_path, project_dir)
                media_tags.append(
                    f'      <audio id="{scene_id}-audio" data-start="{cursor}" data-duration="{dur}" '
                    f'data-track-index="10" src="{rel}"></audio>'
                )
            cursor += dur

        # end card — "Part 2 is coming", shown in the video itself and not only in the caption
        outro = state.get("outro") or {}
        if outro.get("text"):
            odur = float(outro.get("duration_sec", 2.5))
            last_image = (visuals.get(segments[-1]["scene_number"], {}).get("image_url", "")
                          if segments else "")
            backdrop = (f'        <img src="{last_image}" crossorigin="anonymous" />\n'
                        if last_image else "")
            clips.append(
                f'      <section id="outro" class="clip outro" data-start="{cursor}" '
                f'data-duration="{odur}" data-track-index="2">\n'
                f'{backdrop}'
                f'        <p class="outro-text">{outro["text"]}</p>\n'
                f'      </section>'
            )
            tweens.append(
                f'      tl.fromTo("#outro .outro-text", {{ opacity: 0, scale: 0.9 }}, '
                f'{{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.6)" }}, {cursor});\n'
            )
            tweens.append(
                f'      tl.set("#outro .outro-text", {{ opacity: 1 }}, {round(cursor + odur, 2)});\n'
            )
            cursor += odur

        # music mode: one BGM track under the whole video instead of per-scene voiceover
        bgm = state.get("bgm_path", "")
        if bgm and os.path.exists(bgm):
            rel = os.path.relpath(bgm, project_dir)
            media_tags.append(
                f'      <audio id="bgm" data-start="0" data-duration="{cursor}" '
                f'data-track-index="11" data-volume="{bgm_volume}" src="{rel}"></audio>'
            )

        # PART N badge for serialised videos
        part = state.get("part_number", 0)
        part_html = ""
        if part:
            part_html = (
                f'      <div id="part-badge" class="clip part-badge" data-start="0" '
                f'data-duration="{cursor}" data-track-index="21">PART {part}</div>\n'
            )

        html = (
            _HEAD.format(width=width, height=height,
                         title=state["script"].get("title", "Untitled"),
                         comp_id=state["job_id"], duration=cursor,
                         # the corner label would sit on top of the full-frame disclosure card,
                         # which `check` flags as overlapping text — start it after the card
                         label_start=label_start,
                         label_duration=round(cursor - label_start, 2))
            + part_html
            + "\n".join(clips) + "\n" + "\n".join(media_tags) + "\n"
            + _TAIL.format(comp_id=state["job_id"], tweens="".join(tweens))
        )

        os.makedirs(project_dir, exist_ok=True)
        index_path = os.path.join(project_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)
        state["composition_path"] = index_path
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"composition_writer: {e}")
        state["composition_path"] = ""
    return state
