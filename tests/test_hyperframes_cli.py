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


def test_check_builds_expected_command():
    captured = {}
    def fake_run(cmd, capture_output, text):
        captured["cmd"] = cmd
        return FakeResult(0)
    cli = HyperFramesCLI(runner=fake_run)
    cli.check("proj")
    # `check` runs lint + runtime + layout + motion + contrast in one session;
    # `validate` is deprecated in the CLI as of 0.7.76
    assert captured["cmd"] == ["npx", "hyperframes", "check", "proj", "--json"]


def test_legacy_lint_validate_inspect_route_through_check():
    calls = []
    def fake_run(cmd, capture_output, text):
        calls.append(cmd[2])
        return FakeResult(0)
    cli = HyperFramesCLI(runner=fake_run)
    cli.lint("p"); cli.validate("p"); cli.inspect("p")
    assert calls == ["check", "check", "check"]


def test_render_builds_expected_command():
    captured = {}
    def fake_run(cmd, capture_output, text):
        captured["cmd"] = cmd
        return FakeResult(0)
    cli = HyperFramesCLI(runner=fake_run)
    cli.render("proj", "proj/render/final.mp4", quality="high")
    assert captured["cmd"] == ["npx", "hyperframes", "render", "proj",
                              "--quality", "high", "--output", "proj/render/final.mp4"]
