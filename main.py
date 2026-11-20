#!/usr/bin/env python3
"""The World in Brief - 19 November 2026.

A newspaper front page that sums up Thursday 19 November 2026's world news
in one image, drawn entirely by code. Entry for the make.fun bounty
news-image-20261119 ($250).

Python 3, standard library only. Renders a 1024x1024 PNG:

- Masthead with the date THURSDAY, 19 NOVEMBER 2026 set large.
- One lead story (the Shenzhen trilateral summit) plus four more story
  panels, each with a headline, a one-line subline and a small flat
  pictogram drawn with rectangles, circles and lines.
- An IN BRIEF strip with four shorter items, and a sources footer.

No photograph or outside artwork is used anywhere - every pixel is drawn
by this program. No network, no wall clock, no randomness: two runs
produce byte-identical output.

Run it:

    python3 main.py            # writes entry.png to $MAKEFUN_OUTPUT_DIR
                               # (default /output)
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)   # off-white newsprint
INK = (26, 42, 74)        # dark navy ink
INK_SOFT = (74, 88, 118)  # muted navy for sublines
RULE = (26, 42, 74)
RED = (178, 58, 48)
BLUE = (43, 98, 168)
GREEN = (46, 125, 87)
GOLD = (176, 132, 32)
TEAL = (32, 120, 118)
GREY = (120, 120, 112)

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def fill(color):
    px[0:] = bytes(color) * (W * H)


def rect(x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        off = (yy * W + x0) * 3
        px[off:off + len(row)] = row


def hline(x, y, w, color, t=1):
    rect(x, y, w, t, color)


def vline(x, y, h, color, t=1):
    rect(x, y, t, h, color)


def line(x0, y0, x1, y1, color, t=1):
    """Bresenham line with a square brush of thickness t."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    half = t // 2
    while True:
        rect(x0 - half, y0 - half, t, t, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        dx = int((r * r - (yy - cy) ** 2) ** 0.5)
        rect(cx - dx, yy, 2 * dx + 1, 1, color)


def ring(cx, cy, r, color, t=3):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2
            if (r - t) ** 2 <= d2 <= r * r:
                if 0 <= xx < W and 0 <= yy < H:
                    off = (yy * W + xx) * 3
                    px[off:off + 3] = bytes(color)


def triangle(x0, y0, x1, y1, x2, y2, color):
    """Filled triangle via scanline interpolation."""
    pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts
    if ay == cy:
        return
    for y in range(ay, cy + 1):
        if y < by:
            xa = ax + (bx - ax) * (y - ay) / max(1, by - ay)
            xb = ax + (cx - ax) * (y - ay) / (cy - ay)
        else:
            xa = bx + (cx - bx) * (y - by) / max(1, cy - by)
            xb = ax + (cx - ax) * (y - ay) / (cy - ay)
        xlo, xhi = sorted((int(xa), int(xb)))
        rect(xlo, y, xhi - xlo + 1, 1, color)


# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits, '#' = ink. ASCII only, so nothing can
# render garbled.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, color):
    """Draw ALL-CAPS ASCII text; unknown chars become a blank."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    rect(cx + col * scale, y + row * scale,
                         scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(x, y, w, s, scale, color):
    tw = text_width(s, scale)
    draw_text(x + max(0, (w - tw) // 2), y, s, scale, color)


def wrap(s, max_w, scale):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(s, max_w, max_lines, scale, min_scale=1):
    """Wrap at scale, shrinking until it fits max_lines (never below 1)."""
    while scale > min_scale:
        lines = wrap(s, max_w, scale)
        if len(lines) <= max_lines:
            return lines, scale
        scale -= 1
    lines = wrap(s, max_w, scale)
    return lines[:max_lines], scale


def draw_block(x, y, w, s, scale, max_lines, color, leading=None):
    """Wrapped text block; returns the y just below it."""
    lines, sc = fit_lines(s, w, max_lines, scale)
    lh = (leading if leading is not None else 10 * sc)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * lh, ln, sc, color)
    return y + len(lines) * lh


# ---------------------------------------------------------------- pictograms
def icon_summit(x, y, s):
    """Three flags over a globe: the Shenzhen trilateral summit."""
    disc(x + s // 2, y + s // 2, s // 2 - 6, (214, 228, 240))
    ring(x + s // 2, y + s // 2, s // 2 - 6, BLUE, 3)
    line(x + 14, y + s - 18, x + s - 14, y + s - 18, BLUE, 3)
    for i, c in enumerate((RED, BLUE, GOLD)):
        fx = x + 22 + i * 34
        vline(fx, y + 22, 52, INK, 3)
        triangle(fx, y + 22, fx + 26, y + 30, fx, y + 38, c)


def icon_scales(x, y, s):
    """Scales of justice: the ICJ genocide ruling."""
    vline(x + s // 2, y + 12, s - 30, INK, 4)
    hline(x + 16, y + 22, s - 32, INK, 4)
    line(x + 16, y + 22, x + 26, y + 46, INK, 3)
    line(x + s - 16, y + 22, x + s - 26, y + 46, INK, 3)
    triangle(x + 8, y + 46, x + 44, y + 46, x + 26, y + 62, GOLD)
    triangle(x + s - 44, y + 46, x + s - 8, y + 46, x + s - 26, y + 62, GOLD)
    hline(x + s // 2 - 16, y + s - 16, 32, INK, 4)
    disc(x + s // 2, y + 12, 5, RED)


def icon_chart(x, y, s):
    """Rising bars and an arrow: the record IPO against falling markets."""
    base = y + s - 16
    bars = [(18, 26), (40, 44), (62, 34)]
    for i, (bx, bh) in enumerate(bars):
        rect(x + bx, base - bh, 16, bh, (GREEN, BLUE, GOLD)[i])
    line(x + 14, base - 56, x + 34, base - 66, RED, 4)
    line(x + 34, base - 66, x + 52, base - 58, RED, 4)
    line(x + 52, base - 58, x + 74, base - 74, RED, 4)
    triangle(x + 74, base - 74, x + 60, base - 76, x + 70, base - 60, RED)
    hline(x + 10, base, s - 20, INK, 3)


def icon_tanker(x, y, s):
    """A tanker on waves with a flame: the Hormuz attacks."""
    hull_y = y + 52
    triangle(x + 16, hull_y, x + s - 16, hull_y, x + s - 30, hull_y + 22, INK)
    rect(x + 16, hull_y, s - 32, 8, INK)
    rect(x + s // 2 - 4, hull_y - 18, 8, 18, INK)
    triangle(x + s // 2 + 14, hull_y - 34, x + s // 2 + 26, hull_y - 10,
             x + s // 2 + 4, hull_y - 10, RED)
    triangle(x + s // 2 + 18, hull_y - 24, x + s // 2 + 26, hull_y - 10,
             x + s // 2 + 10, hull_y - 10, GOLD)
    for wy in (hull_y + 34, hull_y + 46):
        wave = [(12, wy), (30, wy - 5), (48, wy), (66, wy - 5), (s - 12, wy)]
        for (ax, ay), (bx, by) in zip(wave, wave[1:]):
            line(x + ax, ay, x + bx, by, BLUE, 3)


def icon_bridge(x, y, s):
    """A bridge deck broken in the middle: the Kerch crossing."""
    deck = y + 44
    hline(x + 10, deck, 34, INK, 5)
    hline(x + s - 44, deck, 34, INK, 5)
    line(x + 10, deck, x + 26, deck + 26, INK, 4)
    line(x + s - 10, deck, x + s - 26, deck + 26, INK, 4)
    line(x + 30, deck, x + 44, deck - 12, RED, 4)
    line(x + 58, deck, x + 44, deck - 12, RED, 4)
    line(x + 44, deck - 12, x + 44, deck - 26, RED, 4)
    line(x + 34, deck - 20, x + 54, deck - 4, RED, 3)
    disc(x + 44, deck - 12, 4, GOLD)
    hline(x + 14, deck + 34, s - 28, BLUE, 3)


# ---------------------------------------------------------------- stories
# (kicker, headline, subline, accent, icon)
LEAD = ("SHENZHEN - SUMMIT",
        "TRUMP, XI AND PUTIN ISSUE PEACE DECLARATION",
        "FIRST TRILATERAL SUMMIT OF THE THREE LEADERS ENDS WITH NO ARMS "
        "DEAL AND NO WORD ON THE WARS IN UKRAINE OR IRAN",
        RED, icon_summit)

STORIES = [
    ("THE HAGUE - JUSTICE",
     "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
     "ICJ HOLDS A STATE RESPONSIBLE FOR GENOCIDE FOR THE FIRST TIME OVER "
     "THE 2017 ROHINGYA CAMPAIGN",
     GOLD, icon_scales),
    ("NEW YORK - MARKETS",
     "RECORD ANTHROPIC IPO SOARS AS STOCKS SLIDE",
     "$81.3BN DEBUT JUMPS 34% ON NASDAQ WHILE THE S&P 500 FALLS 2% FOR A "
     "FIFTH STRAIGHT DAY",
     GREEN, icon_chart),
    ("THE GULF - CONFLICT",
     "IRAN WIDENS GULF ATTACKS; TANKERS BURN",
     "STRIKES HIT A US BASE IN KUWAIT AND TARGETS IN BAHRAIN AS HORMUZ "
     "SHIPPING COMES UNDER FIRE",
     RED, icon_tanker),
    ("CRIMEA - WAR",
     "UKRAINE HITS CRIMEAN BRIDGE A THIRD TIME",
     "KERCH CROSSING SHUT AFTER FOUR DAYS OF STRIKES; PUTIN VOWS A "
     "HARSHER RESPONSE",
     BLUE, icon_bridge),
]

BRIEFS = [
    "DENMARK APPROVES GREENLAND-US SECURITY PACT, 109-0",
    "EU PROPOSES A EUR 45BN LOAN TO SUPPORT UKRAINE",
    "VAN GOGH PAINTING SELLS FOR $190.4M, A RECORD",
    "MIGRANT BOAT CAPSIZES OFF SENEGAL; DOZENS MISSING",
]


def story_panel(x, y, w, h, num, kicker, headline, subline, accent, icon):
    rect(x, y, w, h, (255, 255, 255))
    rect(x, y, w, 5, accent)
    # number + icon
    draw_text(x + 14, y + 18, "%02d" % num, 2, INK_SOFT)
    icon(x + 12, y + 48, 92)
    tx = x + 116
    tw = w - 116 - 16
    draw_text(tx, y + 18, kicker, 2, accent)
    y2 = draw_block(tx, y + 44, tw, headline, 3, 2, INK, leading=30)
    draw_block(tx, y2 + 8, tw, subline, 2, 2, INK_SOFT, leading=20)


def main():
    fill(PAPER)
    m = 36                      # margin
    inner = W - 2 * m

    # ---- masthead
    draw_text_centered(m, 34, inner, "THE WORLD IN BRIEF", 6, INK)
    hline(m, 96, inner, RULE, 3)
    draw_text_centered(m, 110, inner, "THURSDAY, 19 NOVEMBER 2026", 3, RED)
    draw_text_centered(m, 140, inner,
                       "THE DAY IN FIVE STORIES", 2, INK_SOFT)
    hline(m, 168, inner, RULE, 2)

    # ---- lead story
    ly, lh = 184, 208
    rect(m, ly, inner, lh, (255, 255, 255))
    rect(m, ly, inner, 6, RED)
    icon_summit(m + 16, ly + 18, 168)
    tx = m + 204
    tw = inner - 204 - 20
    draw_text(tx, ly + 20, LEAD[0], 2, RED)
    y2 = draw_block(tx, ly + 48, tw, LEAD[1], 4, 2, INK, leading=40)
    draw_block(tx, y2 + 10, tw, LEAD[2], 2, 3, INK_SOFT, leading=20)

    # ---- four story panels, 2 x 2
    gy = 408
    gw = (inner - 16) // 2
    gh = 196
    for i, (kicker, headline, subline, accent, icon) in enumerate(STORIES):
        px0 = m + (i % 2) * (gw + 16)
        py0 = gy + (i // 2) * (gh + 16)
        story_panel(px0, py0, gw, gh, i + 2, kicker, headline, subline,
                    accent, icon)

    # ---- in brief strip
    by = 832
    bh = 128
    rect(m, by, inner, bh, (255, 255, 255))
    rect(m, by, inner, 5, INK)
    draw_text(m + 16, by + 16, "IN BRIEF", 2, INK)
    hline(m + 16, by + 40, inner - 32, (200, 196, 182), 1)
    col_w = (inner - 32 - 24) // 2
    for i, b in enumerate(BRIEFS):
        bx = m + 16 + (i % 2) * (col_w + 24)
        byy = by + 54 + (i // 2) * 34
        rect(bx, byy + 2, 8, 8, RED if i % 2 == 0 else BLUE)
        draw_block(bx + 16, byy, col_w - 16, b, 2, 2, INK, leading=18)

    # ---- footer
    hline(m, 976, inner, RULE, 2)
    draw_text_centered(m, 988, inner,
                       "SOURCES: AP - REUTERS - BBC - UN NEWS", 1,
                       INK_SOFT)

    # ---- PNG encode (hand-rolled: IHDR / IDAT / IEND, zlib, CRC32)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)  # filter: none
        raw += px[yy * W * 3:(yy + 1) * W * 3]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes)" % (path, len(png)), file=sys.stderr)
    for s in (LEAD[1],) + tuple(st[1] for st in STORIES):
        for ch in s:
            if ch not in FONT:
                print("WARNING: unrenderable char %r" % ch, file=sys.stderr)


if __name__ == "__main__":
    main()
