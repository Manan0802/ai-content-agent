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
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="{comp_id}" data-start="0" data-width="{width}" data-height="{height}" data-duration="{duration}">
      <div id="ai-label" class="clip ai-label" data-start="0" data-duration="{duration}" data-track-index="20">AI-Generated</div>
"""

_TAIL = """    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["{comp_id}"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


def composition_writer_node(state: ContentState, project_dir: str,
                            width: int = 1080, height: int = 1920,
                            disclosure_duration_sec: float = 3.0) -> ContentState:
    try:
        segments = state["script"]["segments"]
        visuals = {v["scene_number"]: v for v in state.get("visual_assets", [])}
        audio_assets = {a["scene_number"]: a for a in state.get("audio_assets", [])}
        disclosure_audio = state.get("disclosure_audio_path", "")

        clips, media_tags, cursor = [], [], 0.0

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

        for seg in segments:
            dur = float(seg["duration_sec"])
            image = visuals.get(seg["scene_number"], {}).get("image_url", "")
            text = seg.get("voiceover_text", "")
            scene_id = f"scene-{seg['scene_number']}"
            clips.append(
                f'      <section id="{scene_id}" class="clip" data-start="{cursor}" data-duration="{dur}" '
                f'data-track-index="1">\n'
                f'        <img src="{image}" crossorigin="anonymous" />\n'
                f'        <p class="caption">{text}</p>\n'
                f'      </section>'
            )
            audio_path = audio_assets.get(seg["scene_number"], {}).get("audio_path", "")
            if audio_path:
                rel = os.path.relpath(audio_path, project_dir)
                media_tags.append(
                    f'      <audio id="{scene_id}-audio" data-start="{cursor}" data-duration="{dur}" '
                    f'data-track-index="10" src="{rel}"></audio>'
                )
            cursor += dur

        html = (
            _HEAD.format(width=width, height=height,
                         title=state["script"].get("title", "Untitled"),
                         comp_id=state["job_id"], duration=cursor)
            + "\n".join(clips) + "\n" + "\n".join(media_tags) + "\n"
            + _TAIL.format(comp_id=state["job_id"])
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
