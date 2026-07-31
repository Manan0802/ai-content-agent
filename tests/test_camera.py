"""Every scene got the identical 1.0 -> 1.08 push-in, which is why a run of stills reads as a
slideshow no matter how good the images are. A real edit varies the move shot to shot: push in on
a reveal, pull back to show a room, drift across a wide.

This is not the full answer — the reference account generates actual video per scene, and their
character's head physically turns. But varied camera moves cost nothing and remove the metronome.
"""
import pytest
from modules.camera import move_for, MOVES


@pytest.mark.parametrize("n", range(1, 15))
def test_every_scene_gets_a_usable_move(n):
    frm, to = move_for(n)
    assert "scale" in frm and "scale" in to
    for v in (frm, to):
        assert 0.95 <= v["scale"] <= 1.25          # never so far in that the image softens


def test_consecutive_scenes_never_repeat_the_same_move():
    moves = [move_for(n) for n in range(1, 13)]
    for a, b in zip(moves, moves[1:]):
        assert a != b


def test_the_same_scene_always_gets_the_same_move():
    """Re-rendering a part must not silently change its edit."""
    assert move_for(4) == move_for(4)


def test_moves_actually_move():
    for frm, to in MOVES:
        assert frm != to


def test_a_move_is_never_so_fast_it_reads_as_a_jump():
    """Bounds are set against the SHORTEST scene we ever render (2.2s, the music-mode floor) on a
    1080px-wide frame. 80px over 2.2s is ~3.4% of frame width per second — visible, not a whip."""
    SHORTEST_SCENE_SEC = 2.2
    FRAME_W = 1080
    for frm, to in MOVES:
        assert abs(to["scale"] - frm["scale"]) <= 0.14
        for axis in ("x", "y"):
            px = abs(to.get(axis, 0) - frm.get(axis, 0))
            assert px / SHORTEST_SCENE_SEC / FRAME_W <= 0.05
