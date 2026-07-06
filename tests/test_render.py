from orchestrator.state import new_state
from agents.render import render_node


class FakeCLI:
    def __init__(self, fail_at=None):
        self.fail_at = fail_at
        self.calls = []

    def lint(self, d):
        self.calls.append(("lint", d))
        if self.fail_at == "lint":
            raise RuntimeError("lint failed")

    def validate(self, d):
        self.calls.append(("validate", d))

    def inspect(self, d):
        self.calls.append(("inspect", d))

    def render(self, d, out, quality="high"):
        self.calls.append(("render", d, out))


class ApproveNotifier:
    def ask_approval(self, title, preview):
        return "approve"


class RejectNotifier:
    def ask_approval(self, title, preview):
        return "reject"


def _state():
    return new_state("horror", "semi_auto", "hinglish", "short", ["render"])


def test_render_completes_on_approval(monkeypatch):
    import agents.render as render_mod
    monkeypatch.setattr(render_mod.os.path, "exists", lambda p: True)
    monkeypatch.setattr(render_mod.os.path, "getsize", lambda p: 1024)
    out = render_node(_state(), cli=FakeCLI(), notifier=ApproveNotifier(), project_dir="proj")
    assert out["status"] == "media_complete"
    assert out["render_output_path"]


def test_render_fails_fast_on_precheck_error():
    out = render_node(_state(), cli=FakeCLI(fail_at="lint"), notifier=ApproveNotifier(), project_dir="proj")
    assert out["status"] == "failed"
    assert out["errors"]


def test_render_fails_on_reject():
    out = render_node(_state(), cli=FakeCLI(), notifier=RejectNotifier(), project_dir="proj")
    assert out["status"] == "failed"
