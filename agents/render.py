import os
from orchestrator.state import ContentState

# Bound at module level so tests can substitute them without patching the global `os.path`
# (patching os.path.exists globally also breaks os.makedirs, which relies on it internally).
_exists = os.path.exists
_getsize = os.path.getsize


def render_node(state: ContentState, cli, notifier, project_dir: str) -> ContentState:
    try:
        cli.lint(project_dir)
        cli.validate(project_dir)
        cli.inspect(project_dir)
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"render_precheck: {e}")
        state["status"] = "failed"
        return state

    if "render" in state.get("hitl_checkpoints", []) and state["mode"] != "full_auto":
        decision = notifier.ask_approval(
            "Ready to render final video",
            f"Composition passed lint/validate/inspect in {project_dir}. "
            f"Preview with `npx hyperframes preview` before approving if unsure.",
        )
        if decision != "approve":
            state["status"] = "failed"
            return state

    output_path = os.path.join(project_dir, "render", "final.mp4")
    try:
        cli.render(project_dir, output_path, quality="high")
        if not _exists(output_path) or _getsize(output_path) == 0:
            raise RuntimeError("render produced no output")
        state["render_output_path"] = output_path
        state["status"] = "media_complete"
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"render: {e}")
        state["status"] = "failed"
    return state
