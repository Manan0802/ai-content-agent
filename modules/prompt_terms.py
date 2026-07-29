"""Indian/British English -> the English an image model was actually trained on.

The model draws what the caption dataset meant by a word, not what we meant. "Torch" is the one
that bit us: it produced two policemen holding burning wooden brands in the middle of a modern
crime story. Applied when the prompt is built, so it also catches scripts the LLM writes.
"""
import re

# longest first, so "torchlight" is matched before "torch"
_SWAPS = [
    ("torchlight", "flashlight beam"),
    ("torch", "flashlight"),        # British: electric torch. Model: a burning brand.
    ("lorry", "truck"),
    ("lift", "elevator"),           # British: elevator. Model: someone lifting something.
]


def _match_case(original: str, replacement: str) -> str:
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def disambiguate(prompt: str | None) -> str:
    text = prompt or ""
    for bad, good in _SWAPS:
        # \b so "torchbearer" and "lifting" are left alone
        text = re.sub(
            rf"\b{bad}\b",
            lambda m: _match_case(m.group(0), good),
            text,
            flags=re.IGNORECASE,
        )
    return text
