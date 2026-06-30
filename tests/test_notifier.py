from modules.notifier import AutoApproveNotifier, CLINotifier


def test_autoapprove_always_approves():
    assert AutoApproveNotifier().ask_approval("t", "p") == "approve"


def test_cli_notifier_reads_approve():
    n = CLINotifier(input_fn=lambda _: "a", print_fn=lambda *a, **k: None)
    assert n.ask_approval("Topic", "preview text") == "approve"


def test_cli_notifier_reads_reject():
    n = CLINotifier(input_fn=lambda _: "r", print_fn=lambda *a, **k: None)
    assert n.ask_approval("Topic", "preview text") == "reject"
