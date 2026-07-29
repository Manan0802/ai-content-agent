"""Some English words mean different things to an Indian writer and to an image model trained on
American captions. The model wins, every time, because it is the one drawing.

Found in the crime Part 2: the prompt said two policemen with "torch beams crossing" — British
English for a flashlight — and the model drew two men holding burning wooden torches. Modern
Indian police carrying fire breaks the world completely, and the word appears in every part of
the series.

This is a translation problem, not a one-off typo, so it is fixed where prompts are built rather
than by editing each script — the LLM that writes future scripts will make the same mistake.
"""
import pytest
from modules.prompt_terms import disambiguate


@pytest.mark.parametrize("bad,good", [
    ("torch", "flashlight"),
    ("torchlight", "flashlight beam"),
    ("a torch beam across the floor", "a flashlight beam across the floor"),
    ("holding a torch", "holding a flashlight"),
])
def test_torch_becomes_flashlight(bad, good):
    assert disambiguate(bad) == good


def test_case_is_preserved_enough_to_read_naturally():
    assert disambiguate("Torch beam") == "Flashlight beam"


def test_other_indian_english_traps_are_translated():
    assert "elevator" in disambiguate("waiting for the lift")
    assert "truck" in disambiguate("an old lorry on the highway")


def test_a_word_that_merely_contains_a_trap_is_left_alone():
    # "torchbearer" and "lifting" must not be mangled
    assert disambiguate("the torchbearer") == "the torchbearer"
    assert disambiguate("lifting a box") == "lifting a box"


def test_ordinary_prompts_pass_through_untouched():
    p = "Wide shot inside an empty dark Indian living room, a plastic chair knocked over"
    assert disambiguate(p) == p


def test_empty_input_is_safe():
    assert disambiguate("") == ""
    assert disambiguate(None) == ""
