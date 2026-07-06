import pytest
from integrations.hyperframes_cli import HyperFramesCLI


class FakeResult:
    def __init__(self, returncode=0, stderr=""):
        self.returncode = returncode
        self.stderr = stderr


def test_lint_raises_on_failure():
    def fake_run(cmd, capture_output, text):
        return FakeResult(1, "lint error")
    cli = HyperFramesCLI(runner=fake_run)
    with pytest.raises(RuntimeError):
        cli.lint("some/project")


def test_lint_builds_expected_command():
    captured = {}
    def fake_run(cmd, capture_output, text):
        captured["cmd"] = cmd
        return FakeResult(0)
    cli = HyperFramesCLI(runner=fake_run)
    cli.lint("proj")
    assert captured["cmd"] == ["npx", "hyperframes", "lint", "proj", "--json"]


def test_render_builds_expected_command():
    captured = {}
    def fake_run(cmd, capture_output, text):
        captured["cmd"] = cmd
        return FakeResult(0)
    cli = HyperFramesCLI(runner=fake_run)
    cli.render("proj", "proj/render/final.mp4", quality="high")
    assert captured["cmd"] == ["npx", "hyperframes", "render", "proj",
                              "--quality", "high", "--output", "proj/render/final.mp4"]
