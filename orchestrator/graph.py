from functools import partial
from langgraph.graph import StateGraph, END
from orchestrator.state import ContentState
from agents.idea_generator import idea_generator_node
from agents.script_writer import script_writer_node


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
    state["status"] = "complete"
    return state


def build_graph(groq, trends, notifier, checkpoint_path=":memory:"):
    g = StateGraph(ContentState)
    g.add_node("idea_generator", partial(_idea, groq=groq, trends=trends))
    g.add_node("hitl_topic", partial(_hitl_topic, notifier=notifier))
    g.add_node("script_writer", partial(_script, groq=groq))
    g.add_node("hitl_script", partial(_hitl_script, notifier=notifier))

    g.set_entry_point("idea_generator")
    g.add_edge("idea_generator", "hitl_topic")
    g.add_conditional_edges("hitl_topic", _route_after_topic,
                            {"script_writer": "script_writer", END: END})
    g.add_edge("script_writer", "hitl_script")
    g.add_edge("hitl_script", END)
    return g.compile()
