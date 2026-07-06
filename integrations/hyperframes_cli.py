import subprocess


class HyperFramesCLI:
    def __init__(self, runner=subprocess.run):
        self._run = runner

    def _exec(self, args: list[str]) -> None:
        result = self._run(["npx", "hyperframes", *args], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"hyperframes {' '.join(args)} failed: {result.stderr}")

    def lint(self, project_dir: str) -> None:
        self._exec(["lint", project_dir, "--json"])

    def validate(self, project_dir: str) -> None:
        self._exec(["validate", project_dir, "--json"])

    def inspect(self, project_dir: str) -> None:
        self._exec(["inspect", project_dir, "--json"])

    def render(self, project_dir: str, output_path: str, quality: str = "high") -> None:
        self._exec(["render", project_dir, "--quality", quality, "--output", output_path])
