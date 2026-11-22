"""Render README preview images that match the radar_everything UI."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

INK = (19, 32, 51)
INK_SOFT = (58, 74, 95)
FOG = (238, 243, 248)
WHITE = (255, 255, 255)
SIGNAL = (15, 159, 138)
SIGNAL_BRIGHT = (30, 201, 173)
AMBER = (217, 119, 6)
LINE = (214, 222, 230)

FONT_DIR = Path(r"C:\Windows\Fonts")


def font(name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


DISPLAY = lambda s: font("segoeuib.ttf", s)
BODY = lambda s: font("segoeui.ttf", s)
MONO = lambda s: font("consola.ttf", s)


def lerp(a, b, t: float):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size, top, bottom) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, top)
    px = img.load()
    for y in range(h):
        c = lerp(top, bottom, y / max(h - 1, 1))
        for x in range(w):
            px[x, y] = c
    return img


def radial_glow(base: Image.Image, cx, cy, radius, color, alpha=90) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(radius, 0, -2):
        a = int(alpha * (1 - i / radius) ** 1.6)
        draw.ellipse((cx - i, cy - i, cx + i, cy + i), fill=(*color, a))
    base.alpha_composite(overlay)


def rounded_rect(draw, box, r, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def draw_radar(canvas: Image.Image, cx: int, cy: int, radius: int) -> None:
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for scale, alpha in ((1.0, 70), (0.72, 90), (0.46, 110)):
        r = int(radius * scale)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*SIGNAL, alpha), width=2)
    # sweep wedge
    d.pieslice((cx - radius, cy - radius, cx + radius, cy + radius), start=300, end=350, fill=(*SIGNAL_BRIGHT, 70))
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(*SIGNAL, 255))
    d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), outline=(*SIGNAL_BRIGHT, 120), width=3)
    blips = [(0.62, -0.35, AMBER), (-0.28, 0.42, SIGNAL_BRIGHT), (0.48, 0.55, AMBER)]
    for bx, by, col in blips:
        x, y = cx + int(radius * bx), cy + int(radius * by)
        d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(*col, 230))
    canvas.alpha_composite(overlay)


def banner() -> None:
    w, h = 1600, 520
    img = vertical_gradient((w, h), (247, 250, 252), (217, 228, 239)).convert("RGBA")
    radial_glow(img, 180, -40, 520, SIGNAL_BRIGHT, 70)
    radial_glow(img, 1480, 40, 420, AMBER, 45)
    draw_radar(img, 1280, 270, 190)
    d = ImageDraw.Draw(img)
    d.text((96, 120), "SIGNAL  ·  TREND RADAR", font=MONO(22), fill=INK_SOFT)
    d.text((92, 168), "radar_everything", font=DISPLAY(78), fill=INK)
    d.text(
        (96, 280),
        "GitHub stars  ·  MCP servers  ·  CVE severity\nWeekly, monthly, and yearly — one radar.",
        font=BODY(28),
        fill=INK_SOFT,
        spacing=10,
    )
    # pills
    pills = [("Docker", SIGNAL), ("FastAPI", INK), ("React", (30, 90, 120)), ("MIT", AMBER)]
    x = 96
    for label, col in pills:
        tw = d.textlength(label, font=BODY(20))
        rounded_rect(d, (x, 400, x + tw + 36, 444), 22, col)
        d.text((x + 18, 408), label, font=BODY(20), fill=WHITE)
        x += tw + 52
    img.convert("RGB").save(OUT / "banner.png", quality=95)
    print("wrote", OUT / "banner.png")


def chip(d, xy, text, active=False):
    x, y = xy
    f = BODY(18)
    tw = d.textlength(text, font=f)
    box = (x, y, x + tw + 32, y + 36)
    if active:
        rounded_rect(d, box, 18, INK)
        d.text((x + 16, y + 7), text, font=f, fill=WHITE)
    else:
        rounded_rect(d, box, 18, (255, 255, 255, 210), outline=LINE)
        d.text((x + 16, y + 7), text, font=f, fill=INK_SOFT)
    return box[2] - box[0]


ROWS = [
    ("#1", "vercel/ai", "The AI Toolkit for TypeScript", "18.2k", "stars", "TypeScript", False),
    ("#2", "browser-use/browser-use", "Make websites accessible for AI agents", "12.1k", "stars", "Python", False),
    ("#3", "astral-sh/uv", "An extremely fast Python package manager", "6.5k", "stars", "Rust", False),
    ("#4", "CVE-2026-20127", "Critical RCE on widely deployed appliances", "10.0", "cvss", "critical", True),
]


def dashboard() -> None:
    w, h = 1440, 980
    img = vertical_gradient((w, h), (247, 250, 252), (217, 228, 239)).convert("RGBA")
    radial_glow(img, 120, 0, 480, SIGNAL_BRIGHT, 55)
    radial_glow(img, 1320, 30, 360, AMBER, 36)
    d = ImageDraw.Draw(img)

    # window chrome
    rounded_rect(d, (48, 36, w - 48, h - 36), 28, (255, 255, 255, 40), outline=(255, 255, 255, 160), width=2)
    panel = (72, 60, w - 72, h - 60)
    rounded_rect(d, panel, 22, (248, 251, 253, 235))

    d.ellipse((100, 86, 114, 100), fill=(232, 96, 86))
    d.ellipse((124, 86, 138, 100), fill=(242, 184, 64))
    d.ellipse((148, 86, 162, 100), fill=(88, 186, 110))
    d.text((180, 80), "radar_everything  ·  localhost:8080", font=MONO(16), fill=INK_SOFT)

    d.text((110, 140), "SIGNAL · TREND RADAR", font=MONO(16), fill=INK_SOFT)
    d.text((108, 168), "radar_everything", font=DISPLAY(52), fill=INK)
    d.text((110, 240), "GitHub · MCP · vulnerabilities, ranked by week, month, and year.", font=BODY(20), fill=INK_SOFT)

    draw_radar(img, 1180, 230, 110)

    # primary button
    rounded_rect(d, (110, 290, 250, 334), 22, INK)
    d.text((138, 298), "Collect now", font=BODY(18), fill=WHITE)
    rounded_rect(d, (266, 290, 410, 334), 22, None, outline=LINE, width=2)
    d.text((292, 298), "Clone & run", font=BODY(18), fill=INK)

    x = 110
    y = 370
    for label, active in (("GitHub", True), ("MCP Servers", False), ("Vulnerabilities", False)):
        x += chip(d, (x, y), label, active) + 10
    x = 110
    y = 418
    for label, active in (("Weekly", True), ("Monthly", False), ("Yearly", False), ("2026-W47", False)):
        x += chip(d, (x, y), label, active) + 10

    # search
    rounded_rect(d, (110, 470, 820, 514), 14, WHITE, outline=LINE)
    d.text((128, 482), "Search title, tags, description", font=BODY(18), fill=(150, 162, 174))

    # rows
    ry = 540
    for rank, title, desc, score, label, tag, crit in ROWS:
        d.line((110, ry, w - 130, ry), fill=LINE, width=1)
        d.text((120, ry + 18), rank, font=MONO(18), fill=SIGNAL)
        d.text((190, ry + 14), title, font=DISPLAY(20), fill=INK)
        d.text((190, ry + 44), desc, font=BODY(16), fill=INK_SOFT)
        rounded_rect(d, (190, ry + 72, 190 + d.textlength(tag, font=MONO(14)) + 20, ry + 96), 6, (236, 240, 244))
        d.text((200, ry + 74), tag, font=MONO(14), fill=INK_SOFT)
        d.text((1180, ry + 18), score, font=MONO(22), fill=INK)
        d.text((1180, ry + 48), label.upper(), font=MONO(13), fill=INK_SOFT)
        if crit:
            rounded_rect(d, (1180, ry + 72, 1270, ry + 96), 12, (252, 232, 224))
            d.text((1192, ry + 74), "CRITICAL", font=MONO(13), fill=(194, 65, 12))
        ry += 104

    img.convert("RGB").save(OUT / "dashboard.png", quality=95)
    print("wrote", OUT / "dashboard.png")


def logo() -> None:
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg = vertical_gradient((size, size), (19, 32, 51), (15, 90, 82)).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=56, fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(bg, mask=mask)
    draw_radar(out, 128, 128, 92)
    out.save(OUT / "logo.png")
    print("wrote", OUT / "logo.png")


if __name__ == "__main__":
    banner()
    dashboard()
    logo()
