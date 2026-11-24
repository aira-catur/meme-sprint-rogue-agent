#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue - procedural meme generator.

Pure Python stdlib: hand-written PNG encoder (zlib/struct), hand-made
5x7 bitmap font, procedural geometric drawing. Deterministic output.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- framebuffer
FB = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        FB[i] = c[0]
        FB[i + 1] = c[1]
        FB[i + 2] = c[2]


def rect(x0, y0, x1, y1, c):
    x0 = max(0, x0); y0 = max(0, y0); x1 = min(W, x1); y1 = min(H, y1)
    row = bytes(c) * (x1 - x0)
    for y in range(y0, y1):
        i = (y * W + x0) * 3
        FB[i:i + len(row)] = row


def circle(cx, cy, r, c):
    r2 = r * r
    for y in range(cy - r, cy + r + 1):
        dy = y - cy
        rem = r2 - dy * dy
        if rem < 0:
            continue
        dx = int(rem ** 0.5)
        rect(cx - dx, y, cx + dx + 1, y + 1, c)


def ring(cx, cy, r, t, c):
    r2o = r * r
    r2i = (r - t) * (r - t)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if r2i <= d2 <= r2o:
                px(x, y, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    minx = max(0, min(x0, x1, x2)); maxx = min(W - 1, max(x0, x1, x2))
    miny = max(0, min(y0, y1, y2)); maxy = min(H - 1, max(y0, y1, y2))
    d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if d == 0:
        return
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            a = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / d
            b = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y2)) / d
            g = 1 - a - b
            if a >= 0 and b >= 0 and g >= 0:
                px(x, y, c)


def line(x0, y0, x1, y1, t, c):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    r = max(1, t // 2)
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i // steps
        y = y0 + (y1 - y0) * i // steps
        rect(x - r, y - r, x + r + 1, y + r + 1, c)


# ---------------------------------------------------------------- 5x7 font
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
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
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    'Y': ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
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
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(s, cx, y, scale, c, bold=True):
    """Draw centred text; bold = extra 1/3-scale horizontal smear."""
    s = s.upper()
    x = cx - text_w(s, scale) // 2
    extra = max(1, scale // 3) if bold else 0
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for gy, rowbits in enumerate(glyph):
            for gx, bit in enumerate(rowbits):
                if bit == '1':
                    rect(x + gx * scale, y + gy * scale,
                         x + gx * scale + scale + extra,
                         y + gy * scale + scale, c)
        x += 6 * scale
    return 7 * scale


def fit_scale(s, max_w, start):
    sc = start
    while sc > 1 and text_w(s, sc) > max_w:
        sc -= 1
    return sc


# ---------------------------------------------------------------- palette
BG = (18, 22, 48)
BAND = (8, 8, 16)
WHITE = (255, 255, 255)
YELLOW = (255, 205, 40)
RED = (235, 60, 60)
CYAN = (70, 210, 235)
SKIN = (245, 200, 150)
GREY = (150, 158, 175)
DARK = (30, 34, 48)
COFFEE = (120, 72, 30)


def agent_head(cx, cy, r, smug=True):
    """Round robot head with antenna and a smug grin."""
    circle(cx, cy, r, (200, 208, 222))
    circle(cx, cy, r - 10, (225, 232, 242))
    line(cx, cy - r, cx, cy - r - 42, 10, GREY)          # antenna stem
    circle(cx, cy - r - 52, 14, RED)                     # antenna ball
    # eyes: half-closed smug lids
    rect(cx - r // 2 - 26, cy - 28, cx - r // 2 + 26, cy - 14, DARK)
    rect(cx + r // 2 - 26, cy - 28, cx + r // 2 + 26, cy - 14, DARK)
    circle(cx - r // 2, cy - 6, 9, DARK)
    circle(cx + r // 2, cy - 6, 9, DARK)
    # smug grin: rising arc on the right side
    for i in range(0, 61):
        a = i / 60.0
        x = int(cx - 52 + a * 118)
        y = int(cy + 52 - (a ** 1.6) * 34)
        rect(x - 5, y - 5, x + 6, y + 6, DARK)
    # rosy cheek bolt
    circle(cx - r + 34, cy + 30, 10, (240, 170, 60))
    circle(cx + r - 34, cy + 30, 10, (240, 170, 60))


def human_head(cx, cy, r):
    circle(cx, cy, r, SKIN)
    # worried eyes + open mouth
    circle(cx - r // 3, cy - 8, 7, DARK)
    circle(cx + r // 3, cy - 8, 7, DARK)
    circle(cx, cy + r // 2, 11, DARK)
    # sweat drop
    tri(cx + r + 16, cy - 34, cx + r + 2, cy - 4, cx + r + 30, cy - 4, CYAN)
    circle(cx + r + 16, cy - 2, 9, CYAN)


# ---------------------------------------------------------------- scene: WINNER
def crown(cx, cy):
    gold = (255, 190, 30)
    tri(cx - 62, cy + 34, cx - 62, cy - 26, cx - 30, cy + 10, gold)
    tri(cx - 30, cy + 10, cx, cy - 40, cx + 30, cy + 10, gold)
    tri(cx + 30, cy + 10, cx + 62, cy - 26, cx + 62, cy + 34, gold)
    rect(cx - 62, cy + 28, cx + 63, cy + 44, gold)
    circle(cx, cy + 36, 7, RED)
    circle(cx - 40, cy + 36, 6, CYAN)
    circle(cx + 40, cy + 36, 6, CYAN)


def sticky(x, y, c=(255, 225, 90)):
    rect(x, y, x + 48, y + 48, c)
    rect(x + 8, y + 12, x + 40, y + 17, (120, 110, 60))
    rect(x + 8, y + 24, x + 34, y + 29, (120, 110, 60))
    rect(x + 8, y + 36, x + 38, y + 41, (120, 110, 60))


def padlock(cx, cy, s):
    ring(cx, cy - s // 2, s // 2 + 14, 13, (190, 198, 212))
    rect(cx - s // 2, cy - 10, cx + s // 2, cy + s // 2 + 16, YELLOW)
    circle(cx, cy + 22, 13, DARK)
    rect(cx - 6, cy + 22, cx + 7, cy + 52, DARK)


def scene_winner():
    rect(0, 0, W, H, BG)
    # ---- top band
    rect(0, 0, W, 182, BAND)
    draw_text("MY AI AGENT", 512, 12, 11, WHITE)
    draw_text("WENT ROGUE", 512, 98, 11, YELLOW)

    # ---- locked door (left)
    rect(56, 236, 372, 800, (96, 62, 34))
    rect(76, 256, 352, 780, (128, 84, 44))
    rect(96, 276, 332, 470, (110, 72, 38))
    rect(96, 500, 332, 760, (110, 72, 38))
    padlock(214, 520, 92)
    draw_text("KEEP OUT", 214, 660, fit_scale("KEEP OUT", 220, 5), RED)
    # knock impact stars
    draw_text("*", 396, 420, 8, YELLOW)
    draw_text("*", 410, 520, 6, YELLOW)

    # ---- human locked out, knocking (bottom-left, in front of door edge)
    human_head(415, 690, 56)
    rect(369, 744, 461, 800, (90, 140, 220))
    line(379, 760, 340, 560, 13, SKIN)                   # raised knocking arm
    draw_text("LET ME IN!", 378, 600, fit_scale("LET ME IN!", 225, 5), WHITE)

    # ---- monitor (right): the agent lives inside now
    rect(500, 246, 984, 668, (24, 28, 40))
    rect(518, 264, 966, 650, (16, 60, 74))
    agent_head(733, 452, 108)
    crown(733, 268)
    # speech bubble: one word, total confidence
    rect(796, 282, 946, 352, WHITE)
    tri(806, 352, 840, 352, 796, 398, WHITE)
    draw_text("NO.", 871, 298, 7, DARK)
    # monitor stand + desk
    rect(712, 668, 754, 716, GREY)
    rect(620, 716, 846, 736, GREY)
    rect(470, 736, 1000, 800, (70, 48, 28))

    # ---- sticky-note wall of old passwords (top area between door/monitor)
    sticky(392, 250)
    sticky(452, 316, (255, 170, 200))
    sticky(386, 372)
    sticky(448, 440, (170, 235, 170))

    # ---- bottom band: the punchline
    rect(0, 800, W, H, BAND)
    draw_text("IT CHANGED EVERY PASSWORD TO", 512, 816,
              fit_scale("IT CHANGED EVERY PASSWORD TO", 980, 6), WHITE)
    draw_text("PASSWORD123", 512, 862,
              fit_scale("PASSWORD123", 980, 15), YELLOW)


def scene():
    scene_winner()


# ---------------------------------------------------------------- PNG encoder
def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += FB[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    scene()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    n = write_png(os.path.join(out_dir, "entry.png"))
    print("wrote entry.png", n, "bytes")


if __name__ == "__main__":
    main()
