from functools import partial
from langgraph.graph import StateGraph, END
from orchestrator.state import ContentState
from agents.idea_generator import idea_generator_node
from agents.script_writer import script_writer_node
from agents.visuals import visuals_node
from agents.voiceover import voiceover_node
from agents.composition_writer import composition_writer_node
from agents.render import render_node
from agents.uploader import uploader_node
from config import SETTINGS


def _idea(state, groq, trends):
    return idea_generator_node(state, groq=groq, trends=trends)


def _hitl_topic(state, notifier):
    if "topic" not in state.get("hitl_checkpoints", []) or state["mode"] == "full_auto":
        decision = "approve"
    else:
        top = state["topic_candidates"][0]["title"] if state["topic_candidates"] else "(none)"
        preview = "\n".join(
            f"{i+1}. {c.get('title')} (score {c.get('viral_score')})"
            for i, c in enumerate(state["topic_candidates"])
        ) or "no candidates"
        decision = notifier.ask_approval(f"Pick topic — top: {top}", preview)
    if decision == "approve" and state["topic_candidates"]:
        state["topic"] = state["topic_candidates"][0]["title"]
        state["human_approved"]["topic"] = True
    elif decision != "approve":
        state["status"] = "failed"
    return state


def _route_after_topic(state):
    return "script_writer" if state["status"] != "failed" and state["topic"] else END


def _script(state, groq):
    return script_writer_node(state, groq=groq)


def _hitl_script(state, notifier):
    if "script" in state.get("hitl_checkpoints", []) and state["mode"] != "full_auto":
        decision = notifier.ask_approval("Review script", str(state["script"])[:1500])
        if decision != "approve":
            state["status"] = "failed"
    return state


def _route_after_script_hitl(state):
    return "visuals" if state["status"] != "failed" else END


def _visuals(state, fal, project_dir):
    return visuals_node(state, fal=fal, character_ref_url=SETTINGS.character_ref_image_url,
                        project_dir=project_dir)


def _voiceover(state, tts, project_dir):
    return voiceover_node(state, tts=tts, output_dir=f"{project_dir}/assets/audio",
                          disclosure_text=SETTINGS.ai_disclosure_text,
                          music_dir=SETTINGS.music_dir,
                          bgm_mode=SETTINGS.bgm_mode)


def _composition(state, project_dir):
    return composition_writer_node(state, project_dir=project_dir,
                                    width=SETTINGS.video_width, height=SETTINGS.video_height,
                                    disclosure_duration_sec=SETTINGS.ai_disclosure_duration_sec,
                                    bgm_volume=SETTINGS.bgm_volume)


def _render(state, hf_cli, notifier, project_dir):
    return render_node(state, cli=hf_cli, notifier=notifier, project_dir=project_dir)


def _uploader(state, youtube, notifier):
    return uploader_node(state, youtube=youtube, notifier=notifier)


def build_graph(groq, trends, notifier, fal=None, tts=None, hf_cli=None, youtube=None,
                project_dir="outputs/job", checkpoint_path=":memory:",
                entry: str = "idea_generator"):
    g = StateGraph(ContentState)
    g.add_node("idea_generator", partial(_idea, groq=groq, trends=trends))
    g.add_node("hitl_topic", partial(_hitl_topic, notifier=notifier))
    g.add_node("script_writer", partial(_script, groq=groq))
    g.add_node("hitl_script", partial(_hitl_script, notifier=notifier))
    g.add_node("visuals", partial(_visuals, fal=fal, project_dir=project_dir))
    g.add_node("voiceover", partial(_voiceover, tts=tts, project_dir=project_dir))
    g.add_node("composition_writer", partial(_composition, project_dir=project_dir))
    g.add_node("render", partial(_render, hf_cli=hf_cli, notifier=notifier, project_dir=project_dir))
    g.add_node("uploader", partial(_uploader, youtube=youtube, notifier=notifier))

    g.set_entry_point(entry)
    g.add_edge("idea_generator", "hitl_topic")
    g.add_conditional_edges("hitl_topic", _route_after_topic,
                            {"script_writer": "script_writer", END: END})
    g.add_edge("script_writer", "hitl_script")
    g.add_conditional_edges("hitl_script", _route_after_script_hitl,
                            {"visuals": "visuals", END: END})
    g.add_edge("visuals", "voiceover")
    g.add_edge("voiceover", "composition_writer")
    g.add_edge("composition_writer", "render")
    g.add_edge("render", "uploader")
    g.add_edge("uploader", END)
    return g.compile()
