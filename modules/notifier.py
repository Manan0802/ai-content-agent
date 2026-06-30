from typing import Callable, Protocol, runtime_checkable


@runtime_checkable
class Notifier(Protocol):
    def ask_approval(self, title: str, preview: str) -> str:
        """Return 'approve' or 'reject'."""
        ...


class AutoApproveNotifier:
    def ask_approval(self, title: str, preview: str) -> str:
        return "approve"


class CLINotifier:
    def __init__(self, input_fn: Callable[[str], str] = input,
                 print_fn: Callable[..., None] = print):
        self._input = input_fn
        self._print = print_fn

    def ask_approval(self, title: str, preview: str) -> str:
        self._print(f"\n=== {title} ===\n{preview}\n")
        answer = self._input("Approve? [a]pprove / [r]eject: ").strip().lower()
        return "approve" if answer.startswith("a") else "reject"
