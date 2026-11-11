"""The words in "POV: the stadium goes quiet".

Three layers, and no more than three:

    0.0 -  6.8   the hook      POV: YOU'RE RONALDO / One shot. Everyone's watching.
   83.6 - 90.0   the question  Whose POV should we animate next?
    0.0 -  6.8   the honesty   An imagined scenario, not a real match.
   83.6 - 90.0

The hook is the topic as the research desk wrote it down; the question is what the
film actually asks, and it asks it plainly instead of promising a part two. The
third line is not decoration. A film with a real club shirt and a real man's name
in the title needs to say, in the picture and not only in the description, that
nothing in it happened -- so the line rides with every card, small, at the foot of
the frame, the whole time a card is up.

Design notes:

**Text is placed against the picture, not over it.** The hook sits in the empty
night sky above the stand, where the drawing has nothing to say; the question
sits in a soft lower-third because the close-up fills every other part of the
frame. A scrim is only used where it is load-bearing.

**Cards are rendered once, then faded.** Each card is a full-frame RGBA layer
built at import-free call time and cached; a frame only pays for its alpha ramp
and one paste. That is why the post pass is cheap enough to run over an
already-rendered master instead of re-rendering the film.

**Tracking, not stretching.** The headline is set in capitals with a few pixels
between the letters, which is what makes a two-line card read as a title rather
than as a caption. It is drawn a character at a time because PIL has no tracking.
"""

from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

from .film import H, W

# --- timing ---------------------------------------------------------------

HOOK = (0.0, 6.8)
CLOSE = (83.6, 90.0)
RIGHTS = ((0.00, 6.8), (83.6, 90.0))   # exactly the cards' windows
FADE = 0.45

# --- type -----------------------------------------------------------------

_FONT_PATHS = {
    True: (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ),
    False: (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ),
}

_fonts: dict = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _fonts:
        f = None
        for path in _FONT_PATHS[bold]:
            if os.path.exists(path):
                try:
                    f = ImageFont.truetype(path, size)
                    break
                except OSError:
                    f = None
        if f is None:                       # Pillow >= 10 can size the default
            try:
                f = ImageFont.load_default(size=size)
            except TypeError:
                f = ImageFont.load_default()
        _fonts[key] = f
    return _fonts[key]


def _tracked(d, y, text, f, tracking, fill, shadow=None):
    """Centre ``text`` on the frame at row ``y``, letter by letter."""
    widths = [f.getlength(ch) for ch in text]
    total = sum(widths) + tracking * max(len(text) - 1, 0)
    x = (W - total) * 0.5
    passes = [(0, 0, fill)]
    if shadow is not None:
        passes.insert(0, (0, shadow[0], shadow[1]))
    for ch, w in zip(text, widths):
        for dx, dy, col in passes:
            d.text((x + dx, y + dy), ch, font=f, fill=col)
        x += w + tracking
    return total


def _centred(d, y, text, f, fill, shadow=None):
    x = (W - f.getlength(text)) * 0.5
    if shadow is not None:
        d.text((x, y + shadow[0]), text, font=f, fill=shadow[1])
    d.text((x, y), text, font=f, fill=fill)


def _ramp(t, a, b, fade=FADE):
    if t <= a or t >= b:
        return 0.0
    return min(1.0, (t - a) / fade, (b - t) / fade)


# --- cards ----------------------------------------------------------------

_cards: dict = {}


def _card(name):
    """Full-frame RGBA layer for one card, built once."""
    if name in _cards:
        return _cards[name]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    if name == "hook":
        # The push-in crosses a floodlight lamp, and a lamp is white. A band of
        # shade under the type is not styling, it is the reason the title can be
        # read at every frame of its own six seconds.
        layer = _shade(layer, 296, 566, peak=152, ramp=0.34)
        d = ImageDraw.Draw(layer)
        _tracked(d, 352, "POV: YOU'RE RONALDO", font(54, True), 5.0,
                 (247, 244, 236, 255), shadow=(3, (0, 0, 0, 150)))
        _centred(d, 452, "One shot. Everyone's watching.", font(36, False),
                 (232, 228, 219, 240), shadow=(3, (0, 0, 0, 140)))
        _rule(d, 540)

    elif name == "close":
        layer = _shade(layer, 1436, 1868, peak=120, ramp=0.26)
        d = ImageDraw.Draw(layer)
        _centred(d, 1556, "Whose POV should we", font(50, True),
                 (247, 244, 236, 255), shadow=(3, (0, 0, 0, 130)))
        _centred(d, 1622, "animate next?", font(50, True),
                 (247, 244, 236, 255), shadow=(3, (0, 0, 0, 130)))

    elif name == "rights":
        # The line has to be readable over floodlit grass and over a close-up
        # alike, so it carries its own plate instead of trusting the picture.
        text = "An imagined scenario, not a real match."
        f = font(26, False)
        tw = f.getlength(text)
        x0, x1 = (W - tw) * 0.5 - 24, (W + tw) * 0.5 + 24
        d.rounded_rectangle([x0, 1794, x1, 1848], radius=8, fill=(4, 6, 10, 128))
        _centred(d, 1802, text, f, (238, 235, 227, 214))

    _cards[name] = layer
    return layer


def _shade(layer, top, bot, peak=120, ramp=0.28, colour=(6, 9, 14)):
    """A soft band of shade, ramped in and out, returned as a new layer."""
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for y in range(top, bot):
        u = (y - top) / (bot - top)
        a = peak * min(1.0, u / ramp, (1.0 - u) / (ramp * 0.7)) ** 1.2
        bd.line([(0, y), (W, y)], fill=colour + (int(a),))
    return Image.alpha_composite(layer, band)


def _rule(d, y, width=132, alpha=120, colour=(240, 236, 227)):
    """A hairline under a card. Cheap, and it stops the type floating."""
    x0 = (W - width) * 0.5
    d.line([(x0, y), (x0 + width, y)], fill=colour + (alpha,), width=2)


def _paste(img, layer, alpha):
    if alpha <= 0.004:
        return img
    mask = layer.getchannel("A")
    if alpha < 0.999:
        mask = mask.point(lambda v: int(v * alpha))
    img.paste(layer, (0, 0), mask)
    return img


def overlay(img, t):
    """Composite the film's words onto an RGB frame in place."""
    hook = _ramp(t, HOOK[0], HOOK[1])
    _paste(img, _card("hook"), hook)

    close = _ramp(t, CLOSE[0], CLOSE[1])
    _paste(img, _card("close"), close)

    rights = max(_ramp(t, a, b) for a, b in RIGHTS)
    _paste(img, _card("rights"), rights)
    return img


def active(t):
    """True when at least one layer is on screen -- lets callers skip work."""
    return (_ramp(t, HOOK[0], HOOK[1]) > 0.0 or _ramp(t, CLOSE[0], CLOSE[1]) > 0.0)
