"""Per-scene camera moves.

A still with a slow zoom is fine once. Twelve of them, all the same zoom at the same speed, is a
slideshow — the eye locks onto the metronome instead of the story. Real edits change the move
every shot, so this cycles push-in, pull-back and drifts.

Deterministic by scene number: re-rendering a part must produce the same edit.
"""

# (from, to) — scale plus optional x/y drift in px, applied to the scene's <img>
MOVES: list[tuple[dict, dict]] = [
    ({"scale": 1.00, "x": 0,   "y": 0},  {"scale": 1.10, "x": 0,   "y": 0}),   # push in
    ({"scale": 1.12, "x": 0,   "y": 0},  {"scale": 1.02, "x": 0,   "y": 0}),   # pull back
    ({"scale": 1.08, "x": -40, "y": 0},  {"scale": 1.08, "x": 40,  "y": 0}),   # drift right
    ({"scale": 1.06, "x": 0,   "y": 30}, {"scale": 1.14, "x": 0,   "y": -20}), # rise + push
    ({"scale": 1.08, "x": 40,  "y": 0},  {"scale": 1.08, "x": -40, "y": 0}),   # drift left
    ({"scale": 1.14, "x": 0,   "y": -25},{"scale": 1.04, "x": 0,   "y": 25}),  # sink + pull
]


def move_for(scene_number: int) -> tuple[dict, dict]:
    return MOVES[(max(scene_number, 1) - 1) % len(MOVES)]
