#!/usr/bin/env python3
"""Build entry.png: Tuesday 17 November 2026 world-news front page (stdlib only)."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# High-contrast newsprint palette
PAPER = (244, 240, 230)
INK = (18, 18, 18)
RULE = (40, 40, 40)
ACCENT = (160, 28, 28)
SEA = (196, 214, 224)
LAND = (92, 118, 92)
LAND_EDGE = (55, 78, 55)
PIN = (190, 24, 24)
MUTED = (70, 70, 70)
PANEL = (232, 226, 214)

# Compact 5x7 glyphs for A-Z, 0-9, punctuation (1 = ink)
_GLYPHS: dict[str, list[str]] = {
    " ": ["00000"] * 7,
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10001", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10001", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "00100", "00100", "01000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "/": ["00001", "00010", "00100", "01000", "10000", "00000", "00000"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    ";": ["00000", "01100", "01100", "00000", "00100", "00100", "01000"],
    "|": ["00100", "00100", "00100", "00100", "00100", "00100", "00100"],
    "·": ["00000", "00000", "01100", "01100", "00000", "00000", "00000"],
}


def _px(buf: bytearray, x: int, y: int, rgb: tuple[int, int, int]) -> None:
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i : i + 3] = bytes(rgb)


def fill_rect(
    buf: bytearray, x0: int, y0: int, x1: int, y1: int, rgb: tuple[int, int, int]
) -> None:
    x0, x1 = max(0, x0), min(W, x1)
    y0, y1 = max(0, y0), min(H, y1)
    row = bytes(rgb) * (x1 - x0)
    for y in range(y0, y1):
        start = (y * W + x0) * 3
        buf[start : start + len(row)] = row


def hline(buf: bytearray, x0: int, x1: int, y: int, rgb: tuple[int, int, int], thick: int = 1) -> None:
    for t in range(thick):
        fill_rect(buf, x0, y + t, x1, y + t + 1, rgb)


def vline(buf: bytearray, x: int, y0: int, y1: int, rgb: tuple[int, int, int], thick: int = 1) -> None:
    for t in range(thick):
        fill_rect(buf, x + t, y0, x + t + 1, y1, rgb)


def text_width(s: str, scale: int, tracking: int = 1) -> int:
    return len(s) * (5 * scale + tracking) - tracking


def draw_text(
    buf: bytearray,
    s: str,
    x: int,
    y: int,
    scale: int,
    rgb: tuple[int, int, int],
    tracking: int = 1,
) -> int:
    cx = x
    for ch in s.upper():
        g = _GLYPHS.get(ch, _GLYPHS["?"])
        for gy, row in enumerate(g):
            for gx, bit in enumerate(row):
                if bit == "1":
                    fill_rect(
                        buf,
                        cx + gx * scale,
                        y + gy * scale,
                        cx + (gx + 1) * scale,
                        y + (gy + 1) * scale,
                        rgb,
                    )
        cx += 5 * scale + tracking
    return cx


def draw_text_fit(
    buf: bytearray,
    s: str,
    x: int,
    y: int,
    max_w: int,
    scale: int,
    rgb: tuple[int, int, int],
    tracking: int = 1,
) -> int:
    """Shrink scale until the string fits max_w; return scale used."""
    sc = scale
    while sc > 2 and text_width(s, sc, tracking) > max_w:
        sc -= 1
    draw_text(buf, s, x, y, sc, rgb, tracking)
    return sc


def wrap_words(s: str, max_chars: int) -> list[str]:
    words = s.split()
    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        trial = (" ".join(cur + [w])).upper()
        if len(trial) <= max_chars:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def draw_wrapped(
    buf: bytearray,
    s: str,
    x: int,
    y: int,
    max_w: int,
    scale: int,
    rgb: tuple[int, int, int],
    line_gap: int = 4,
) -> int:
    max_chars = max(4, max_w // (5 * scale + 1))
    lines = wrap_words(s, max_chars)
    yy = y
    for line in lines:
        draw_text(buf, line, x, yy, scale, rgb)
        yy += 7 * scale + line_gap
    return yy


def fill_poly(buf: bytearray, pts: list[tuple[int, int]], rgb: tuple[int, int, int]) -> None:
    if len(pts) < 3:
        return
    ys = [p[1] for p in pts]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        xs: list[float] = []
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            if y0 == y1:
                continue
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            fill_rect(buf, int(xs[i]), y, int(xs[i + 1]) + 1, y + 1, rgb)


def lonlat_to_xy(lon: float, lat: float, mx: int, my: int, mw: int, mh: int) -> tuple[int, int]:
    x = mx + int((lon + 180.0) / 360.0 * mw)
    y = my + int((90.0 - lat) / 180.0 * mh)
    return x, y


def draw_map(buf: bytearray, mx: int, my: int, mw: int, mh: int) -> None:
    fill_rect(buf, mx, my, mx + mw, my + mh, SEA)
    hline(buf, mx, mx + mw, my, LAND_EDGE, 2)
    hline(buf, mx, mx + mw, my + mh - 2, LAND_EDGE, 2)
    vline(buf, mx, my, my + mh, LAND_EDGE, 2)
    vline(buf, mx + mw - 2, my, my + mh, LAND_EDGE, 2)

    # Coarse continent silhouettes (lon/lat rings)
    continents: list[list[tuple[float, float]]] = [
        # North America
        [(-168, 72), (-140, 70), (-120, 60), (-95, 50), (-80, 45), (-70, 45), (-65, 55),
         (-60, 47), (-82, 30), (-97, 25), (-110, 22), (-125, 35), (-130, 50), (-155, 60), (-168, 72)],
        # South America
        [(-80, 12), (-70, 5), (-60, -5), (-55, -20), (-50, -35), (-70, -55), (-75, -40),
         (-80, -20), (-82, 0), (-80, 12)],
        # Europe
        [(-10, 58), (5, 58), (20, 60), (30, 55), (40, 45), (25, 40), (10, 38), (-5, 36),
         (-10, 43), (-9, 52), (-10, 58)],
        # Africa
        [(-17, 35), (12, 37), (32, 31), (43, 11), (51, -5), (40, -25), (32, -34),
         (18, -34), (12, -15), (8, 5), (-5, 6), (-15, 16), (-17, 35)],
        # Asia (incl. Middle East / India / China / Siberia)
        [(28, 42), (45, 55), (70, 68), (105, 72), (140, 68), (170, 62), (175, 50),
         (145, 42), (130, 35), (122, 22), (105, 8), (88, 8), (78, 20), (68, 28),
         (55, 28), (48, 36), (40, 38), (28, 42)],
        # Australia
        [(114, -14), (134, -11), (148, -18), (152, -32), (142, -39), (122, -36),
         (114, -26), (114, -14)],
        # Greenland
        [(-55, 72), (-40, 75), (-25, 72), (-30, 65), (-45, 62), (-55, 68), (-55, 72)],
    ]
    for ring in continents:
        pts = [lonlat_to_xy(lon, lat, mx, my, mw, mh) for lon, lat in ring]
        fill_poly(buf, pts, LAND)

    # Story pins (lon, lat, label)
    pins = [
        (56.0, 26.5, "1"),   # Hormuz / Qeshm
        (34.5, 45.3, "2"),   # Crimea bridge
        (121.0, 14.6, "3"),  # Manila ASEAN
        (28.9, 47.0, "4"),   # Moldova
        (35.4, 31.8, "5"),   # West Bank / Jericho
        (51.4, 35.7, "6"),   # Iran protests
        (106.9, 47.9, "7"),  # Mongolia
        (-75.7, 45.4, "8"),  # Canada (Carney/Xi tariff story)
        (30.7, 36.9, "9"),   # Antalya COP31
    ]
    for lon, lat, label in pins:
        px, py = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        fill_rect(buf, px - 7, py - 7, px + 8, py + 8, PIN)
        hline(buf, px - 8, px + 9, py - 8, INK, 1)
        hline(buf, px - 8, px + 9, py + 8, INK, 1)
        vline(buf, px - 8, py - 8, py + 9, INK, 1)
        vline(buf, px + 8, py - 8, py + 9, INK, 1)
        draw_text(buf, label, px - 3, py - 5, 2, (255, 255, 255), 0)


def write_png(path: Path, buf: bytearray) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data) & 0xFFFFFFFF
        )

    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(buf[y * W * 3 : (y + 1) * W * 3])
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(
        b"IDAT", zlib.compress(bytes(raw), 9)
    ) + chunk(b"IEND", b"")
    path.write_bytes(png)


def build() -> None:
    buf = bytearray(W * H * 3)
    fill_rect(buf, 0, 0, W, H, PAPER)

    # Outer margin rule
    hline(buf, 28, W - 28, 24, INK, 3)
    hline(buf, 28, W - 28, H - 28, INK, 3)
    vline(buf, 28, 24, H - 28, INK, 3)
    vline(buf, W - 31, 24, H - 28, INK, 3)

    # Masthead
    draw_text(buf, "THE WORLD BRIEF", 48, 42, 6, INK, 2)
    draw_text(buf, "TUESDAY 17 NOVEMBER 2026", 48, 92, 3, ACCENT, 1)
    draw_text(buf, "ONE PAGE  ·  WORLD EDITION", 620, 96, 2, MUTED, 1)
    hline(buf, 40, W - 40, 124, INK, 4)
    hline(buf, 40, W - 40, 132, INK, 1)

    # Lead story
    y = 148
    y = draw_wrapped(
        buf,
        "US STRIKES QESHM AFTER HORMUZ MINE FIRES",
        48,
        y,
        920,
        5,
        INK,
        6,
    )
    y = draw_wrapped(
        buf,
        "Five ships burn in Strait; Iran drones hit Bahrain radar; US jets hit missile sites",
        48,
        y + 4,
        920,
        2,
        MUTED,
        4,
    )

    hline(buf, 40, W - 40, y + 10, RULE, 2)
    body_top = y + 24

    # Map panel (right)
    map_x, map_y, map_w, map_h = 520, body_top, 456, 280
    fill_rect(buf, map_x - 8, map_y - 28, map_x + map_w + 8, map_y + map_h + 8, PANEL)
    draw_text(buf, "WHERE TODAY'S NEWS HIT", map_x, map_y - 22, 2, INK, 1)
    draw_map(buf, map_x, map_y, map_w, map_h)

    # Second lead + side column (left of map)
    col_w = 450
    yy = body_top
    draw_text(buf, "2  CRIMEA BRIDGE SEVERED", 48, yy, 3, INK, 1)
    yy += 28
    yy = draw_wrapped(
        buf,
        "Ukraine hails strike on Kerch link; Russia reports huge drone wave, Kyiv under fire",
        48,
        yy,
        col_w,
        2,
        MUTED,
        3,
    )
    yy += 14
    draw_text(buf, "3  TRUMP IN MANILA", 48, yy, 3, INK, 1)
    yy += 28
    yy = draw_wrapped(
        buf,
        "ASEAN stop before Shenzhen talks with Xi and Putin; Kim meeting floated",
        48,
        yy,
        col_w,
        2,
        MUTED,
        3,
    )
    yy += 14
    draw_text(buf, "4  MOLDOVA SHUTS SKY", 48, yy, 3, INK, 1)
    yy += 28
    yy = draw_wrapped(
        buf,
        "Airspace closed after Shahed-type drone toward Chisinau; Sandu blames Russia war spillover",
        48,
        yy,
        col_w,
        2,
        MUTED,
        3,
    )

    # Bottom band of regional briefs
    band_y = max(yy, map_y + map_h) + 28
    hline(buf, 40, W - 40, band_y, INK, 3)
    band_y += 16
    draw_text(buf, "AROUND THE WORLD", 48, band_y, 3, ACCENT, 1)
    band_y += 34

    briefs = [
        ("5 WEST BANK", "Settlers kill woman near Jericho; UK sanctions settlement builders"),
        ("6 IRAN STREETS", "Anti-regime protests erupt after deadly bus crash"),
        ("7 MONGOLIA", "President Khurelsukh says he will resign amid graft claims"),
        ("8 CANADA-CHINA", "Xi and Carney deepen ties with fresh tariff cuts"),
        ("9 COP31 ANTALYA", "Climate talks press AI energy use; US data centers near Denmark's CO2"),
        ("10 CHIP WAR", "US tightens foreign data-center rules to curb China AI compute"),
    ]

    left_x = 48
    right_x = 536
    row_h = 70
    for i, (title, deck) in enumerate(briefs):
        col = i % 2
        row = i // 2
        x = left_x if col == 0 else right_x
        yb = band_y + row * row_h
        draw_text(buf, title, x, yb, 2, INK, 1)
        draw_wrapped(buf, deck, x, yb + 22, 430, 2, MUTED, 3)

    # Footer
    hline(buf, 40, W - 40, H - 56, RULE, 2)
    draw_text(
        buf,
        "SOURCES: REUTERS · EURONEWS · DEMOCRACY NOW · JUST SECURITY · XINHUA  |  EVENTS FROM 13-17 NOV 2026",
        48,
        H - 46,
        1,
        MUTED,
        1,
    )

    out = Path(__file__).resolve().parent / "entry.png"
    write_png(out, buf)
    size = out.stat().st_size
    print(f"wrote {out} ({size} bytes, {W}x{H})")
    if size > 1024 * 1024:
        raise SystemExit("entry.png exceeds 1 MiB")


if __name__ == "__main__":
    build()
