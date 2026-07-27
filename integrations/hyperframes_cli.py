import subprocess


class HyperFramesCLI:
    def __init__(self, runner=subprocess.run):
        self._run = runner

    def _exec(self, args: list[str]) -> None:
        result = self._run(["npx", "hyperframes", *args], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"hyperframes {' '.join(args)} failed: {result.stderr}")

    def check(self, project_dir: str) -> None:
        """One browser session that runs lint + runtime + layout + motion + WCAG checks.

        Replaces the separate lint/validate/inspect calls — `validate` is deprecated in the
        CLI (verified 2026-07-22 against hyperframes 0.7.76) and `check` covers all of them.
        """
        self._exec(["check", project_dir, "--json"])

    # kept so older callers/tests keep working; all three now route through `check`
    def lint(self, project_dir: str) -> None:
        self.check(project_dir)

    def validate(self, project_dir: str) -> None:
        self.check(project_dir)

    def inspect(self, project_dir: str) -> None:
        self.check(project_dir)

    def render(self, project_dir: str, output_path: str, quality: str = "high") -> None:
        self._exec(["render", project_dir, "--quality", quality, "--output", output_path])
