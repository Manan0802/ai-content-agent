import os
from orchestrator.state import ContentState

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
      .speaker {{ display: block; font-size: 30px; font-weight: 700; color: #ffd54a;
                  -webkit-text-stroke: 2px #000; margin-bottom: 10px; }}
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
                            bgm_volume: float = 0.25) -> ContentState:
    try:
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
            speaker_name = names.get(seg.get("speaker"), "") if show_speaker else ""
            scene_id = f"scene-{seg['scene_number']}"
            speaker_html = (
                f'<span class="speaker">{speaker_name}</span>' if speaker_name else ""
            )
            clips.append(
                f'      <section id="{scene_id}" class="clip" data-start="{cursor}" data-duration="{dur}" '
                f'data-track-index="1">\n'
                f'        <img src="{image}" crossorigin="anonymous" />\n'
                f'        <div class="scrim"></div>\n'
                f'        <p class="dialogue">{speaker_html}{text}</p>\n'
                f'      </section>'
            )
            # motion: slow push-in on the image + dialogue fading up.
            # Also required for correctness — an empty timeline never advances under seek and
            # `hyperframes check` fails the whole run with `sweep_static`.
            tweens.append(
                f'      tl.fromTo("#{scene_id} img", {{ scale: 1.0 }}, '
                f'{{ scale: 1.08, duration: {dur}, ease: "none" }}, {cursor});\n'
            )
            tweens.append(
                f'      tl.fromTo("#{scene_id} .dialogue", {{ opacity: 0, y: 30 }}, '
                f'{{ opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }}, {cursor});\n'
            )
            # crossfade in/out so scenes flow instead of hard-cutting
            if seg is not segments[0]:
                tweens.append(
                    f'      tl.fromTo("#{scene_id}", {{ opacity: 0 }}, '
                    f'{{ opacity: 1, duration: 0.35, ease: "power1.inOut" }}, {cursor});\n'
                )
            tweens.append(
                f'      tl.to("#{scene_id} .dialogue", '
                f'{{ opacity: 0, duration: 0.25 }}, {round(cursor + dur - 0.25, 2)});\n'
            )
            # hard kill on the clip boundary — a seek that lands past the fade would otherwise
            # leave the previous scene's text visible (`gsap_exit_missing_hard_kill`)
            tweens.append(
                f'      tl.set("#{scene_id} .dialogue", '
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
