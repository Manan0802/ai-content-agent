"""Burned Hindi has to be shaped, not just drawn glyph by glyph.

Pillow only reorders Devanagari when it was built against libraqm. Without it, a pre-base
`ि` matra stays where it sits in the codepoint order, so `किसनै` renders as `कसिनै` — a real
end card shipped that way before anyone noticed. Nothing errors, nothing warns; the video just
has wrong Hindi in it.

`pip install Pillow` grabs a wheel that has no raqm, so this can come back at any time on a
fresh checkout or after an unrelated reinstall. Fix:

    brew install libraqm
    pip install --force-reinstall --no-binary :all: --no-cache-dir Pillow
"""
import pytest
from PIL import Image, ImageDraw, ImageFont, features

from modules.assemble import _DEVANAGARI


def test_pillow_has_raqm():
    assert features.check("raqm"), (
        "Pillow has no libraqm, so burned Devanagari will be mis-shaped "
        "(किसनै renders as कसिनै). See this module's docstring for the fix."
    )


def test_pre_base_matra_is_reordered():
    """`कि` must draw the ि to the LEFT of the क, which is not the codepoint order."""
    font = ImageFont.truetype(_DEVANAGARI, 80)
    img = Image.new("L", (400, 140), 0)
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "कि", font=font, fill=255)

    ink = img.getbbox()
    assert ink is not None, "nothing was drawn"

    # With shaping, the matra sits before the consonant, so ink starts at the left edge of the
    # draw position. Unshaped, the ि trails the क and the glyph cluster is measurably wider.
    bare = Image.new("L", (400, 140), 0)
    ImageDraw.Draw(bare).text((20, 20), "क", font=font, fill=255)
    bare_ink = bare.getbbox()

    shaped_width = ink[2] - ink[0]
    bare_width = bare_ink[2] - bare_ink[0]
    assert shaped_width < bare_width * 2, (
        f"'कि' drew {shaped_width}px against a bare 'क' at {bare_width}px — the matra was "
        "appended rather than reordered, which means shaping is off"
    )
