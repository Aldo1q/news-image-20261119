#!/usr/bin/env python3
"""Generate the entry image for make.fun's news-image-20261119 bounty.

The entry is a single square image: a newspaper front page that sums up
19 November 2026. This second version is built around one idea -- win the
two-second glance. A slim nameplate, one dominant illustration (the flags
of the United States, China and Russia flying over a drawn Shenzhen
skyline at dusk), a two-line lead headline set very large, one black
markets band whose numerals do the talking, four compact briefs, and a
black world-briefs ticker. Everything else from the first version --
the extra photo caption boxes, the why-it-matters panel, the thin chart
line, the dense grey columns -- is gone.

The page is drawn entirely in code with PIL. No external image is read,
and the only randomness comes from a fixed seed, so two runs produce
byte-identical output. The finished page is written to ``entry.png``
inside the output directory (``MAKEFUN_OUTPUT_DIR`` when set, otherwise
``/output``). If PIL is somehow unavailable at run time, the program
falls back to validating the ``entry.png`` shipped beside it -- which is
the exact output of this generator -- and copying those bytes instead,
so the entry still produces its promised image.

Stories carried, all from 19 November 2026: the first Trump-Xi-Putin
trilateral in Shenzhen; Brent crude down 2.6% to $89.59 with the VIX at
24.56; Anthropic's record IPO ($83 a share, $81.3 billion raised, a
$1.5 trillion valuation); the ICJ Rohingya genocide ruling; the Crimea
Bridge hit for the third time; the IMF putting global debt near 100% of
GDP; and the world briefs rail (IEA on Hormuz, EU aid for Ukraine,
COP31, the Van Gogh record, Bangladesh, Fiji).
"""

import hashlib
import math
import os
import random
import struct
import sys

CANVAS = 1024
MARGIN = 46
X0 = MARGIN
X1 = CANVAS - MARGIN
WIDTH = X1 - X0  # 932

PAPER = (246, 241, 231)
INK = (17, 17, 17)
INK_SOFT = (43, 40, 36)
GREY = (96, 92, 84)
FAINT = (178, 170, 156)
RED = (176, 18, 27)
RED_BRIGHT = (255, 107, 94)
BAND = (17, 18, 22)
BAND_LABEL = (168, 172, 180)

SERIF_BLACK = "NotoSerif-Black.ttf"
SERIF_COND_BLACK = "NotoSerif-CondensedBlack.ttf"
SERIF_BOLD = "NotoSerif-Bold.ttf"
SERIF = "NotoSerif-Regular.ttf"
SANS_BLACK = "NotoSans-Black.ttf"
SANS_BOLD = "NotoSans-Bold.ttf"
SANS = "NotoSans-Regular.ttf"

_FONT_CACHE = {}


def _find_font(filename):
    """Locate a font file under the usual system font roots."""
    roots = ("/usr/share/fonts", "/usr/local/share/fonts",
             os.path.expanduser("~/.fonts"))
    for root in roots:
        for dirpath, _dirs, files in os.walk(root):
            if filename in files:
                return os.path.join(dirpath, filename)
    return None


def font(filename, size):
    """Load a TrueType font, cached by (file, size), DejaVu as fallback."""
    key = (filename, size)
    if key not in _FONT_CACHE:
        from PIL import ImageFont
        path = _find_font(filename) or _find_font("DejaVuSerif-Bold.ttf") \
            or _find_font("DejaVuSans-Bold.ttf")
        _FONT_CACHE[key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[key]


def tracked_width(draw, text, fnt, tracking):
    """Width of text drawn letter by letter with extra tracking."""
    return sum(draw.textlength(ch, font=fnt) for ch in text) \
        + tracking * max(0, len(text) - 1)


def draw_tracked(draw, x, y, text, fnt, fill, tracking=0,
                 center_at=None, right_at=None):
    """Draw letterspaced text; optionally centre or right-align it."""
    total = tracked_width(draw, text, fnt, tracking)
    if center_at is not None:
        x = center_at - total / 2
    if right_at is not None:
        x = right_at - total
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=fnt, fill=fill)
        cx += draw.textlength(ch, font=fnt) + tracking
    return total


def fit_font(draw, filename, text, max_width, size, tracking=0, floor=10):
    """Largest size at or below ``size`` whose tracked width fits."""
    while size > floor:
        fnt = font(filename, size)
        if tracked_width(draw, text, fnt, tracking) <= max_width:
            return fnt, size
        size -= 2
    return font(filename, floor), floor


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap against a pixel width."""
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- hero

def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _star(draw, cx, cy, radius, fill, rot=-math.pi / 2):
    """A five-pointed star as a ten-vertex polygon."""
    pts = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * 0.382
        a = rot + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill)


def _flag_art(kind, w, h):
    """Draw one flag flat, at full size, ready to be waved."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)
    if kind == "us":
        stripe = h / 13.0
        for i in range(13):
            if i % 2 == 0:
                d.rectangle([0, i * stripe, w, (i + 1) * stripe],
                            fill=(179, 34, 52))
        canton_w, canton_h = int(w * 0.42), int(stripe * 7)
        d.rectangle([0, 0, canton_w, canton_h], fill=(10, 49, 97))
        rows, cols = 9, 6
        for r in range(rows):
            n = cols if r % 2 == 0 else cols - 1
            for c in range(n):
                cx = canton_w * (c + (0.5 if r % 2 == 0 else 1.0)) / cols
                cy = canton_h * (r + 0.5) / rows
                d.ellipse([cx - 2.6, cy - 2.6, cx + 2.6, cy + 2.6],
                          fill=(255, 255, 255))
    elif kind == "cn":
        d.rectangle([0, 0, w, h], fill=(222, 41, 16))
        yellow = (255, 222, 0)
        _star(d, 30, 30, 17, yellow)
        for sx, sy in ((60, 11), (72, 28), (72, 47), (60, 64)):
            _star(d, sx, sy, 6.5, yellow)
    else:  # ru
        third = h / 3.0
        d.rectangle([0, 0, w, third], fill=(255, 255, 255))
        d.rectangle([0, third, w, 2 * third], fill=(0, 57, 166))
        d.rectangle([0, 2 * third, w, h], fill=(213, 43, 30))
    return img


def _wave(flag, amp=5, wavelength=95.0, phase=0.0):
    """Give a flat flag a fabric wave: sine lift plus column shading."""
    from PIL import Image, ImageEnhance
    w, h = flag.size
    out = Image.new("RGBA", (w, h + 2 * amp + 2), (0, 0, 0, 0))
    for col in range(w):
        angle = 2 * math.pi * (col / wavelength) + phase
        shift = int(round(amp * math.sin(angle)))
        shade = 0.84 + 0.16 * (0.5 + 0.5 * math.sin(angle + 0.9))
        strip = flag.crop((col, 0, col + 1, h))
        strip = ImageEnhance.Brightness(strip).enhance(shade)
        out.paste(strip, (col, amp + shift))
    return out


def draw_hero(img, x0, y0, w, h):
    """The dominant visual: three flags over a Shenzhen dusk skyline."""
    from PIL import Image, ImageDraw
    d = ImageDraw.Draw(img, "RGBA")
    stops = [(0.00, (13, 24, 48)), (0.45, (30, 52, 92)),
             (0.72, (94, 74, 84)), (0.88, (196, 110, 58)),
             (1.00, (224, 150, 76))]
    for row in range(h):
        t = row / max(1, h - 1)
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                d.line([(x0, y0 + row), (x0 + w, y0 + row)],
                       fill=_lerp(c0, c1, (t - t0) / (t1 - t0)))
                break
    horizon = y0 + h - 28

    # Low sun and its halo, right of centre, behind the towers.
    sun_x, sun_y = x0 + int(w * 0.66), horizon - 24
    d.ellipse([sun_x - 62, sun_y - 62, sun_x + 62, sun_y + 62],
              fill=(244, 190, 110, 56))
    d.ellipse([sun_x - 30, sun_y - 30, sun_x + 30, sun_y + 30],
              fill=(246, 199, 116))

    # Skyline silhouette with lit windows; one tapered supertall.
    rng = random.Random(20261119)
    silhouette = (8, 10, 14)
    window_tones = [(255, 214, 130), (255, 190, 105), (240, 225, 180)]
    towers = []
    tx = x0 + 4
    while tx < x0 + w - 30:
        tw = rng.randint(26, 58)
        th = rng.randint(36, 126)
        towers.append((tx, tw, th))
        tx += tw + rng.randint(2, 10)
    for tx, tw, th in towers:
        d.rectangle([tx, horizon - th, tx + tw, horizon], fill=silhouette)
        for _ in range(th // 8):
            wx = rng.randint(tx + 3, tx + tw - 5)
            wy = rng.randint(horizon - th + 4, horizon - 6)
            d.rectangle([wx, wy, wx + 2, wy + 3],
                        fill=rng.choice(window_tones))
    tall_x = x0 + int(w * 0.60)
    d.polygon([(tall_x, horizon), (tall_x + 56, horizon),
               (tall_x + 36, horizon - 196), (tall_x + 20, horizon - 196)],
              fill=silhouette)
    d.line([(tall_x + 28, horizon - 196), (tall_x + 28, horizon - 224)],
           fill=silhouette, width=3)
    for _ in range(46):
        wx = rng.randint(tall_x + 6, tall_x + 48)
        wy = rng.randint(horizon - 188, horizon - 8)
        d.rectangle([wx, wy, wx + 2, wy + 3],
                    fill=rng.choice(window_tones))

    # Foreground plaza the flagpoles stand on.
    d.rectangle([x0, horizon, x0 + w, y0 + h], fill=(6, 8, 11))

    # Three flagpoles with waved flags: the page's colour anchor.
    flag_w, flag_h = 196, 118
    for i, kind in enumerate(("us", "cn", "ru")):
        pole_x = x0 + 250 + i * 216
        top = y0 + 30
        d.line([(pole_x, top), (pole_x, horizon + 14)],
               fill=(216, 216, 222), width=4)
        d.ellipse([pole_x - 4, top - 5, pole_x + 4, top + 3],
                  fill=(212, 175, 55))
        flag = _wave(_flag_art(kind, flag_w, flag_h), phase=i * 1.7)
        alpha = flag.split()[3].point(lambda a: int(a * 0.38))
        shadow = Image.new("RGBA", flag.size, (0, 0, 0, 255))
        shadow.putalpha(alpha)
        img.paste(shadow, (pole_x + 9, top + 13), shadow)
        img.paste(flag, (pole_x + 4, top + 6), flag)

    d.rectangle([x0, y0, x0 + w, y0 + h], outline=(10, 10, 10), width=2)


# ------------------------------------------------------------- the page

def draw_masthead(d):
    """Folio line, slim nameplate, double rule."""
    f = font(SANS_BOLD, 16)
    d.line([(X0, 24), (X1, 24)], fill=INK, width=2)
    draw_tracked(d, X0, 31, "WORLD EDITION", f, INK, tracking=2)
    draw_tracked(d, 0, 31, "Thursday, 19 November 2026", f, INK,
                 tracking=2, center_at=CANVAS // 2)
    draw_tracked(d, 0, 31, "VOL. 1 · NO. 25 · PAGE 1", f, INK,
                 tracking=2, right_at=X1)
    d.line([(X0, 57), (X1, 57)], fill=INK, width=1)
    name = "THE WORLD IN ONE IMAGE"
    fnt, _ = fit_font(d, SERIF_BLACK, name, 880, 60)
    w = d.textlength(name, font=fnt)
    d.text(((CANVAS - w) / 2, 66), name, font=fnt, fill=INK)
    d.line([(X0, 133), (X1, 133)], fill=INK, width=3)
    d.line([(X0, 139), (X1, 139)], fill=INK, width=1)


def draw_lead(d):
    """Red kicker, the giant two-line headline, and a two-line deck."""
    hero_caption = ("THE FLAGS OF THE UNITED STATES, CHINA AND RUSSIA "
                    "OVER SHENZHEN'S CONVENTION DISTRICT · ILLUSTRATION")
    draw_tracked(d, 0, 390, hero_caption, font(SANS_BOLD, 13), GREY,
                 tracking=1, center_at=CANVAS // 2)
    draw_tracked(d, 0, 420, "FIRST-EVER TRILATERAL · SHENZHEN · APEC",
                 font(SANS_BLACK, 20), RED, tracking=3,
                 center_at=CANVAS // 2)
    lines = ("TRUMP, XI, PUTIN", "THE FIRST TRILATERAL")
    fnt, size = fit_font(d, SERIF_COND_BLACK, lines[1], WIDTH, 108)
    y = 448
    for line in lines:
        w = d.textlength(line, font=fnt)
        d.text(((CANVAS - w) / 2, y), line, font=fnt, fill=INK)
        y += int(size * 0.99)
    deck = ("The US, Chinese and Russian leaders sit down together "
            "for the first time.",
            "Ukraine, nuclear arms and the Strait of Hormuz share "
            "one table.")
    fd = font(SERIF, 23)
    y += 6
    for line in deck:
        w = d.textlength(line, font=fd)
        d.text(((CANVAS - w) / 2, y), line, font=fd, fill=INK_SOFT)
        y += 28


def draw_markets(d, top):
    """One black band; the numerals do the talking."""
    d.rectangle([X0, top, X1, top + 74], fill=BAND)
    draw_tracked(d, X0 + 22, top + 14, "MARKETS", font(SANS_BLACK, 17),
                 (255, 255, 255), tracking=2)
    d.text((X0 + 22, top + 42), "Stocks fall in Europe and Asia",
           font=font(SANS, 13), fill=BAND_LABEL)
    stats = (("BRENT CRUDE", "-2.6%", RED_BRIGHT),
             ("CLOSE, A BARREL", "$89.59", (255, 255, 255)),
             ("VIX · FEAR INDEX", "24.56", (255, 255, 255)))
    x = X0 + 252
    for label, value, colour in stats:
        draw_tracked(d, x, top + 8, label, font(SANS_BOLD, 11),
                     BAND_LABEL, tracking=1)
        d.text((x, top + 24), value, font=font(SANS_BLACK, 40),
               fill=colour)
        x += 228


def draw_briefs(d, top):
    """Four compact briefs in hairline-separated columns."""
    cols = (
        ("TECHNOLOGY", "ANTHROPIC'S RECORD IPO",
         "$83 · $81.3B · $1.5T",
         "Share price, raised, valuation — the largest debut ever "
         "recorded."),
        ("JUSTICE", "WORLD COURT'S GENOCIDE RULING",
         None,
         "Gambia's case against Myanmar over the crackdown that "
         "drove 730,000 Rohingya into Bangladesh."),
        ("WAR IN UKRAINE", "CRIMEA BRIDGE HIT FOR THE THIRD TIME",
         None,
         "Traffic suspended after two nights of strikes on the "
         "bridge to annexed Crimea."),
        ("THE WORLD ECONOMY", "IMF: GLOBAL DEBT NEARS 100% OF GDP",
         None,
         "Public debt rivals the world's entire output — less room "
         "to answer the next crisis."),
    )
    gutter = 18
    col_w = (WIDTH - gutter * 3) // 4
    fh = font(SERIF_BOLD, 19)
    fd = font(SERIF, 13)
    for i, (label, head, stat, deck) in enumerate(cols):
        x = X0 + i * (col_w + gutter)
        if i:
            d.line([(x - gutter // 2, top), (x - gutter // 2, top + 118)],
                   fill=FAINT, width=1)
        draw_tracked(d, x, top, label, font(SANS_BLACK, 12), RED,
                     tracking=1)
        y = top + 20
        for line in wrap(d, head, fh, col_w):
            d.text((x, y), line, font=fh, fill=INK)
            y += 22
        y = max(y + 4, top + 70)
        if stat:
            d.text((x, y), stat, font=font(SANS_BLACK, 17), fill=INK)
            y += 22
        for line in wrap(d, deck, fd, col_w):
            d.text((x, y), line, font=fd, fill=INK_SOFT)
            y += 16


def draw_ticker(d, top):
    """The world briefs rail: white type on a black strip, two lines."""
    d.rectangle([X0, top, X1, top + 40], fill=BAND)
    text = ("WORLD BRIEFS — IEA: HORMUZ CRISIS THE GRAVEST "
            "ENERGY-SECURITY THREAT EVER SEEN · EU: €45 BILLION MORE "
            "FOR UKRAINE · COP31 MINISTERS RACE TO UNBLOCK CLIMATE "
            "TEXT, ANTALYA · VAN GOGH FETCHES RECORD $190.4 MILLION · "
            "BANGLADESH: YUNUS HOME TORCHED · FIJI DECLARES DROUGHT "
            "DISASTER")
    size = 13
    while size > 10:
        fnt = font(SANS_BOLD, size)
        lines = wrap(d, text, fnt, WIDTH - 28)
        if len(lines) <= 2:
            break
        size -= 1
    y = top + 5
    for line in lines[:2]:
        w = d.textlength(line, font=fnt)
        d.text(((CANVAS - w) / 2, y), line, font=fnt,
               fill=(255, 255, 255))
        y += 17


def build_image():
    """Compose the whole front page and return it as an image."""
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (CANVAS, CANVAS), PAPER + (255,))
    d = ImageDraw.Draw(img, "RGBA")
    draw_masthead(d)
    draw_hero(img, X0, 148, WIDTH, 236)
    draw_lead(d)
    draw_markets(d, 748)
    draw_briefs(d, 834)
    draw_ticker(d, 966)
    return img.convert("RGB")


# ------------------------------------------------------- shipped fallback

def _shipped_png_bytes():
    """Validate the shipped entry.png and return its bytes, or exit."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "entry.png")
    if not os.path.isfile(path):
        print("no entry.png beside main.py and PIL unavailable",
              file=sys.stderr)
        sys.exit(1)
    with open(path, "rb") as handle:
        data = handle.read()
    signature = b"\x89PNG\r\n\x1a\n"
    if data[:8] != signature or len(data) < 33:
        print("shipped entry.png is not a PNG", file=sys.stderr)
        sys.exit(1)
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (CANVAS, CANVAS):
        print("shipped entry.png is %dx%d, expected %dx%d"
              % (width, height, CANVAS, CANVAS), file=sys.stderr)
        sys.exit(1)
    return data


def main():
    try:
        from PIL import Image  # noqa: F401
        data_holder = {}
        img = build_image()
        import io
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        data = buffer.getvalue()
        data_holder["how"] = "generated"
    except ImportError:
        data = _shipped_png_bytes()
        data_holder = {"how": "shipped fallback"}

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, "entry.png")
    with open(destination, "wb") as handle:
        handle.write(data)
    print("wrote %s (%s, %d bytes, sha256 %s)"
          % (destination, data_holder["how"], len(data),
             hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
