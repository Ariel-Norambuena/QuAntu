#!/usr/bin/env python3
"""Render a self-contained workshop video explaining a 87Rb MOT.

The animation is intentionally schematic, but every visual stage follows the
correct physical logic: SAS frequency referencing, red-detuned Doppler cooling,
an anti-Helmholtz quadrupole field, and damped stochastic capture in a MOT.

The only non-standard Python dependencies are NumPy, Pillow and imageio-ffmpeg.
"""

from __future__ import annotations

import argparse
import math
import subprocess
import sys
import wave
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


DESIGN_W = 1920
DESIGN_H = 1080
TOTAL_DURATION = 98.0
SCENES = (
    (0.0, 6.0, "INTRO"),
    (6.0, 23.0, "SAS"),
    (23.0, 42.0, "DOPPLER"),
    (42.0, 59.0, "B FIELD"),
    (59.0, 84.0, "MOT CAPTURE"),
    (84.0, 98.0, "COLD CLOUD"),
)


COLORS = {
    "bg0": (4, 8, 22),
    "bg1": (9, 18, 43),
    "white": (238, 246, 255),
    "muted": (143, 164, 195),
    "cyan": (62, 226, 255),
    "blue": (69, 123, 255),
    "violet": (170, 93, 255),
    "magenta": (255, 76, 190),
    "red": (255, 68, 91),
    "orange": (255, 157, 70),
    "gold": (255, 213, 112),
    "green": (91, 238, 168),
    "panel": (12, 25, 53),
    "line": (58, 83, 124),
}


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return min(hi, max(lo, x))


def smooth(x: float) -> float:
    x = clamp(x)
    return x * x * (3.0 - 2.0 * x)


def ease_out(x: float) -> float:
    x = clamp(x)
    return 1.0 - (1.0 - x) ** 3


def pulse(x: float) -> float:
    return 0.5 - 0.5 * math.cos(2.0 * math.pi * x)


def rgba(color: tuple[int, int, int], alpha: int | float = 255):
    return (*color, int(clamp(float(alpha), 0, 255)))


@dataclass
class Canvas:
    width: int
    height: int

    def __post_init__(self):
        self.scale = self.width / DESIGN_W
        if abs(self.height / DESIGN_H - self.scale) > 1e-3:
            raise ValueError("The renderer requires a 16:9 canvas.")
        self.font_paths = {
            "regular": Path(r"C:\Windows\Fonts\segoeui.ttf"),
            "bold": Path(r"C:\Windows\Fonts\segoeuib.ttf"),
            "light": Path(r"C:\Windows\Fonts\segoeuil.ttf"),
            "mono": Path(r"C:\Windows\Fonts\consola.ttf"),
        }
        self.font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
        self.background = self._make_background()

    def p(self, x: float, y: float) -> tuple[int, int]:
        return int(round(x * self.scale)), int(round(y * self.scale))

    def s(self, value: float) -> int:
        return max(1, int(round(value * self.scale)))

    def font(self, size: int, face: str = "regular"):
        key = (face, self.s(size))
        if key not in self.font_cache:
            path = self.font_paths.get(face, self.font_paths["regular"])
            # Keep the original Windows appearance when available, then try
            # common Linux/macOS fonts and Pillow's portable default.
            filenames = {
                "regular": ("DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Arial.ttf"),
                "bold": ("DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "Arial Bold.ttf"),
                "light": ("DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Arial.ttf"),
                "mono": ("DejaVuSansMono.ttf", "LiberationMono-Regular.ttf", "Menlo.ttc"),
            }
            names = filenames.get(face, filenames["regular"])
            roots = (
                Path("/usr/share/fonts/truetype/dejavu"),
                Path("/usr/share/fonts/truetype/liberation2"),
                Path("/Library/Fonts"),
                Path("/System/Library/Fonts"),
            )
            candidates = [str(path), r"C:\Windows\Fonts\arial.ttf", *names]
            candidates.extend(str(root / name) for root in roots for name in names)
            for candidate in candidates:
                try:
                    self.font_cache[key] = ImageFont.truetype(candidate, key[1])
                    break
                except OSError:
                    continue
            else:
                self.font_cache[key] = ImageFont.load_default(size=key[1])
        return self.font_cache[key]

    def _make_background(self) -> Image.Image:
        yy, xx = np.mgrid[0 : self.height, 0 : self.width]
        x = xx / max(self.width - 1, 1)
        y = yy / max(self.height - 1, 1)
        radial = np.exp(-(((x - 0.51) / 0.72) ** 2 + ((y - 0.44) / 0.82) ** 2))
        cyan_haze = np.exp(-(((x - 0.08) / 0.28) ** 2 + ((y - 0.17) / 0.35) ** 2))
        violet_haze = np.exp(-(((x - 0.92) / 0.34) ** 2 + ((y - 0.72) / 0.44) ** 2))
        arr = np.zeros((self.height, self.width, 3), dtype=np.float32)
        arr[:] = np.array(COLORS["bg0"], dtype=np.float32)
        arr += radial[..., None] * np.array((7, 13, 27), dtype=np.float32)
        arr += cyan_haze[..., None] * np.array((0, 10, 17), dtype=np.float32)
        arr += violet_haze[..., None] * np.array((9, 2, 16), dtype=np.float32)
        vignette = np.clip(1.15 - 0.62 * ((x - 0.5) ** 2 + (y - 0.5) ** 2), 0.76, 1.0)
        arr *= vignette[..., None]
        # Keep the working canvas in RGB. ImageDraw(..., "RGBA") then performs
        # true alpha blending; drawing directly on an RGBA canvas would preserve
        # semi-transparent pixels that later become incorrectly saturated when
        # converted to H.264's RGB input.
        return Image.fromarray(np.uint8(np.clip(arr, 0, 255)), "RGB")


class EquationAtlas:
    """Load LaTeX-rendered equations and tint/scale them for the current frame."""

    def __init__(self):
        self.root = Path(__file__).resolve().parent / "assets" / "equations"
        self.source_cache: dict[str, Image.Image] = {}
        self.render_cache: dict[tuple, Image.Image] = {}

    def get(self, key: str, height: int, color, alpha: int = 255) -> Image.Image:
        cache_key = (key, height, tuple(color), int(alpha))
        if cache_key in self.render_cache:
            return self.render_cache[cache_key]
        if key not in self.source_cache:
            path = self.root / f"{key}.png"
            if not path.exists():
                raise FileNotFoundError(
                    f"Missing LaTeX asset {path}. Run make_latex_assets.py first."
                )
            self.source_cache[key] = Image.open(path).convert("RGBA")
        source = self.source_cache[key]
        width = max(1, int(round(source.width * height / source.height)))
        scaled = source.resize((width, height), Image.Resampling.LANCZOS)
        source_alpha = np.asarray(scaled.getchannel("A"), dtype=np.float32)
        source_alpha *= clamp(alpha, 0, 255) / 255.0
        tinted = Image.new("RGBA", scaled.size, (*color, 0))
        tinted.putalpha(Image.fromarray(np.uint8(np.clip(source_alpha, 0, 255))))
        self.render_cache[cache_key] = tinted
        return tinted


EQUATIONS = EquationAtlas()


def latex(im, canvas: Canvas, key: str, xy, height: float, color=COLORS["white"], anchor="mm", alpha=255):
    equation = EQUATIONS.get(key, canvas.s(height), color, int(alpha))
    x, y = canvas.p(*xy)
    horizontal = anchor[0] if anchor else "l"
    vertical = anchor[1] if len(anchor) > 1 else "t"
    if horizontal == "m":
        x -= equation.width // 2
    elif horizontal == "r":
        x -= equation.width
    if vertical == "m":
        y -= equation.height // 2
    elif vertical == "b":
        y -= equation.height
    im.paste(equation, (x, y), equation)


def equation_badge(im, draw, canvas, box, key, height, color, alpha=255):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        [canvas.p(x0, y0), canvas.p(x1, y1)],
        radius=canvas.s((y1 - y0) * 0.28),
        fill=rgba(color, int(alpha * 0.11)),
        outline=rgba(color, int(alpha * 0.52)),
        width=canvas.s(1.4),
    )
    latex(im, canvas, key, ((x0 + x1) / 2, (y0 + y1) / 2), height, color, "mm", alpha)


def text(
    draw: ImageDraw.ImageDraw,
    canvas: Canvas,
    xy: tuple[float, float],
    value: str,
    size: int,
    color: tuple[int, int, int] = COLORS["white"],
    face: str = "regular",
    anchor: str = "la",
    alpha: int = 255,
    stroke: int = 0,
):
    draw.text(
        canvas.p(*xy),
        value,
        font=canvas.font(size, face),
        fill=rgba(color, alpha),
        anchor=anchor,
        stroke_width=canvas.s(stroke) if stroke else 0,
        stroke_fill=rgba(COLORS["bg0"], alpha),
    )


def multiline(
    draw: ImageDraw.ImageDraw,
    canvas: Canvas,
    xy: tuple[float, float],
    value: str,
    size: int,
    color: tuple[int, int, int] = COLORS["white"],
    face: str = "regular",
    spacing: int = 12,
    alpha: int = 255,
    anchor: str = "la",
):
    draw.multiline_text(
        canvas.p(*xy),
        value,
        font=canvas.font(size, face),
        fill=rgba(color, alpha),
        spacing=canvas.s(spacing),
        anchor=anchor,
    )


def panel(draw: ImageDraw.ImageDraw, canvas: Canvas, box, alpha=210, radius=26, outline_alpha=95):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        [canvas.p(x0, y0), canvas.p(x1, y1)],
        radius=canvas.s(radius),
        fill=rgba(COLORS["panel"], alpha),
        outline=rgba(COLORS["line"], outline_alpha),
        width=canvas.s(1.4),
    )


def line(draw, canvas, pts, fill, width=2):
    draw.line([canvas.p(x, y) for x, y in pts], fill=fill, width=canvas.s(width), joint="curve")


def arrow(draw, canvas, a, b, color, width=6, head=18, alpha=255):
    ax, ay = a
    bx, by = b
    line(draw, canvas, [a, b], rgba(color, alpha), width)
    ang = math.atan2(by - ay, bx - ax)
    h = head
    p1 = (bx - h * math.cos(ang - 0.52), by - h * math.sin(ang - 0.52))
    p2 = (bx - h * math.cos(ang + 0.52), by - h * math.sin(ang + 0.52))
    draw.polygon([canvas.p(bx, by), canvas.p(*p1), canvas.p(*p2)], fill=rgba(color, alpha))


def pill(draw, canvas, xy, label, color, alpha=255, width=None):
    x, y = xy
    font = canvas.font(24, "bold")
    bbox = draw.textbbox((0, 0), label, font=font)
    w = width or ((bbox[2] - bbox[0]) / canvas.scale + 54)
    draw.rounded_rectangle(
        [canvas.p(x, y), canvas.p(x + w, y + 48)],
        radius=canvas.s(24),
        fill=rgba(color, int(alpha * 0.16)),
        outline=rgba(color, int(alpha * 0.62)),
        width=canvas.s(1.5),
    )
    text(draw, canvas, (x + w / 2, y + 24), label, 24, color, "bold", "mm", alpha)


def section_title(draw, canvas, number, kicker, title_value, subtitle, alpha=255):
    text(draw, canvas, (112, 112), number, 24, COLORS["cyan"], "bold", alpha=alpha)
    text(draw, canvas, (170, 112), kicker.upper(), 22, COLORS["muted"], "bold", alpha=alpha)
    text(draw, canvas, (112, 177), title_value, 54, COLORS["white"], "bold", alpha=alpha)
    text(draw, canvas, (114, 260), subtitle, 25, COLORS["muted"], "regular", alpha=alpha)


def timeline(draw, canvas, t):
    y = 1012
    x0, x1 = 112, 1808
    draw.line([canvas.p(x0, y), canvas.p(x1, y)], fill=rgba(COLORS["line"], 100), width=canvas.s(2))
    progress = clamp(t / TOTAL_DURATION)
    draw.line(
        [canvas.p(x0, y), canvas.p(x0 + (x1 - x0) * progress, y)],
        fill=rgba(COLORS["cyan"], 220),
        width=canvas.s(3),
    )
    for start, end, label in SCENES:
        x = x0 + (x1 - x0) * (start / TOTAL_DURATION)
        active = start <= t < end or (t >= TOTAL_DURATION and end == TOTAL_DURATION)
        r = 6 if active else 4
        draw.ellipse(
            [canvas.p(x - r, y - r), canvas.p(x + r, y + r)],
            fill=rgba(COLORS["cyan"] if active else COLORS["line"], 235),
        )
        if active:
            text(draw, canvas, (x, y - 23), label, 16, COLORS["cyan"], "bold", "ms")


def frame_shell(canvas: Canvas, t: float) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = canvas.background.copy()
    draw = ImageDraw.Draw(im, "RGBA")
    # Fine technical grid.
    for x in range(0, DESIGN_W + 1, 120):
        draw.line([canvas.p(x, 0), canvas.p(x, DESIGN_H)], fill=(45, 79, 119, 11), width=1)
    for y in range(0, DESIGN_H + 1, 120):
        draw.line([canvas.p(0, y), canvas.p(DESIGN_W, y)], fill=(45, 79, 119, 11), width=1)
    text(draw, canvas, (1808, 63), "MOT · ⁸⁷Rb · D₂ 780.24 nm", 18, COLORS["muted"], "bold", "ra", 170)
    if t >= 5.5:
        timeline(draw, canvas, t)
    return im, draw


def atom(draw, canvas, xy, radius=10, alpha=255, core=COLORS["gold"]):
    x, y = xy
    for k, a in ((2.8, 22), (1.8, 50)):
        r = radius * k
        draw.ellipse([canvas.p(x - r, y - r), canvas.p(x + r, y + r)], fill=rgba(core, int(a * alpha / 255)))
    r = radius
    draw.ellipse([canvas.p(x - r, y - r), canvas.p(x + r, y + r)], fill=rgba(core, alpha))
    hr = radius * 0.35
    draw.ellipse([canvas.p(x - hr * 1.2, y - hr * 1.3), canvas.p(x + hr * 0.2, y - hr * 0.1)], fill=(255, 255, 245, int(alpha * 0.8)))


def draw_intro(canvas: Canvas, t: float) -> Image.Image:
    im, draw = frame_shell(canvas, t)
    u = clamp(t / 6.0)
    fade = int(255 * smooth(min(u / 0.17, (1 - u) / 0.12 if u > 0.88 else 1)))
    # Orbital motif.
    cx, cy = 960, 390
    for j, (rx, ry, col) in enumerate(((250, 72, COLORS["cyan"]), (170, 170, COLORS["violet"]), (78, 250, COLORS["magenta"]))):
        pts = []
        angle0 = t * (0.22 + j * 0.07)
        for k in range(100):
            q = 2 * math.pi * k / 99
            x = cx + rx * math.cos(q) * math.cos(angle0) - ry * math.sin(q) * math.sin(angle0)
            y = cy + 0.48 * (rx * math.cos(q) * math.sin(angle0) + ry * math.sin(q) * math.cos(angle0))
            pts.append((x, y))
        line(draw, canvas, pts, rgba(col, int(fade * 0.42)), 2)
        q = (u * 1.4 + j / 3) * 2 * math.pi
        atom(draw, canvas, (cx + rx * math.cos(q), cy + 0.48 * ry * math.sin(q)), 7, fade, col)
    atom(draw, canvas, (cx, cy), 22, fade, COLORS["gold"])
    text(draw, canvas, (960, 650), "FROM A THERMAL VAPOR", 27, COLORS["cyan"], "bold", "mm", fade)
    text(draw, canvas, (960, 715), "to a trapped cloud", 67, COLORS["white"], "bold", "mm", fade)
    text(draw, canvas, (960, 789), "A visual guide to a magneto-optical trap", 29, COLORS["muted"], "regular", "mm", fade)
    pill(draw, canvas, (748, 850), "⁸⁷Rb · D₂ · 780 nm", COLORS["violet"], fade, 424)
    return im


def sas_profile(x: float) -> float:
    broad = 0.86 * math.exp(-(x / 0.78) ** 2)
    dips = 0.0
    for c, a, w in ((-0.46, 0.18, 0.035), (-0.12, 0.24, 0.028), (0.30, 0.34, 0.026), (0.58, 0.15, 0.035)):
        dips += a * math.exp(-((x - c) / w) ** 2)
    return broad - dips


def draw_cell(draw, canvas, t, alpha=255):
    x0, y0, x1, y1 = 180, 384, 875, 684
    panel(draw, canvas, (x0, y0, x1, y1), alpha=120, radius=34)
    # Glass cell.
    draw.rounded_rectangle(
        [canvas.p(310, 454), canvas.p(735, 610)],
        radius=canvas.s(58),
        fill=(40, 95, 122, int(alpha * 0.12)),
        outline=rgba(COLORS["cyan"], int(alpha * 0.56)),
        width=canvas.s(3),
    )
    draw.rectangle([canvas.p(274, 487), canvas.p(326, 575)], fill=(20, 48, 69, int(alpha * 0.7)), outline=rgba(COLORS["cyan"], int(alpha * 0.35)))
    draw.rectangle([canvas.p(719, 487), canvas.p(771, 575)], fill=(20, 48, 69, int(alpha * 0.7)), outline=rgba(COLORS["cyan"], int(alpha * 0.35)))
    rng = np.random.default_rng(137)
    for i in range(47):
        bx = rng.uniform(340, 706)
        by = rng.uniform(478, 585)
        x = bx + 7 * math.sin(t * (0.9 + (i % 7) * 0.13) + i)
        y = by + 5 * math.cos(t * (0.7 + (i % 5) * 0.11) + i * 1.7)
        atom(draw, canvas, (x, y), 2.3, int(alpha * 0.72), COLORS["gold"])
    text(draw, canvas, (522, 638), "rubidium vapor cell", 21, COLORS["muted"], "regular", "mm", alpha)


def draw_sas(canvas: Canvas, t: float) -> Image.Image:
    im, draw = frame_shell(canvas, t)
    local = t - 6.0
    u = clamp(local / 17.0)
    scene_alpha = int(255 * smooth(min(local / 0.7, (17 - local) / 0.7)))
    section_title(draw, canvas, "01", "frequency reference", "First: lock the laser frequency", "Saturated absorption spectroscopy (SAS)", scene_alpha)
    draw_cell(draw, canvas, t, scene_alpha)

    # Counterpropagating pump and probe beams.
    beam_a = int(scene_alpha * smooth((local - 1.3) / 1.0))
    for yy, direction, col in ((512, 1, COLORS["red"]), (548, -1, COLORS["cyan"])):
        if direction > 0:
            arrow(draw, canvas, (145, yy), (820, yy), col, 5, 20, beam_a)
        else:
            arrow(draw, canvas, (820, yy), (145, yy), col, 5, 20, beam_a)
    text(draw, canvas, (205, 485), "PUMP", 17, COLORS["red"], "bold", alpha=beam_a)
    text(draw, canvas, (810, 583), "PROBE", 17, COLORS["cyan"], "bold", "ra", beam_a)
    # Laser and detector modules.
    panel(draw, canvas, (130, 714, 433, 848), alpha=180, radius=18)
    text(draw, canvas, (158, 746), "COOLING LASER", 17, COLORS["muted"], "bold", alpha=scene_alpha)
    latex(im, canvas, "nu_lock", (285, 798), 27, COLORS["white"], "mm", scene_alpha)
    text(draw, canvas, (285, 833), "atomic reference", 15, COLORS["muted"], "regular", "mm", scene_alpha)
    draw.rounded_rectangle([canvas.p(481, 738), canvas.p(620, 824)], radius=canvas.s(14), fill=rgba(COLORS["cyan"], 26), outline=rgba(COLORS["cyan"], 110))
    text(draw, canvas, (550, 780), "PID", 29, COLORS["cyan"], "bold", "mm", scene_alpha)
    arrow(draw, canvas, (435, 780), (478, 780), COLORS["cyan"], 3, 13, scene_alpha)
    arrow(draw, canvas, (620, 780), (620, 690), COLORS["cyan"], 3, 13, scene_alpha)

    # Spectrum card.
    panel(draw, canvas, (955, 319, 1782, 850), alpha=205, radius=30)
    text(draw, canvas, (1000, 359), "SAS SIGNAL", 18, COLORS["muted"], "bold", alpha=scene_alpha)
    gx0, gy0, gx1, gy1 = 1020, 760, 1726, 421
    line(draw, canvas, [(gx0, gy1), (gx0, gy0), (gx1, gy0)], rgba(COLORS["line"], scene_alpha), 2)
    text(draw, canvas, (1328, 806), "detuning", 20, COLORS["muted"], "regular", "rm", scene_alpha)
    latex(im, canvas, "detuning_axis", (1347, 806), 22, COLORS["muted"], "lm", scene_alpha)
    text(draw, canvas, (987, 587), "absorption", 18, COLORS["muted"], "regular", "mm", scene_alpha)
    # Broad Doppler envelope.
    broad_pts = []
    sas_pts = []
    reveal = smooth((local - 2.4) / 2.0)
    for i in range(241):
        x = -1 + 2 * i / 240
        xx = gx0 + (gx1 - gx0) * i / 240
        broad = 0.86 * math.exp(-(x / 0.78) ** 2)
        prof = sas_profile(x)
        broad_pts.append((xx, gy0 - (gy0 - gy1) * broad))
        sas_pts.append((xx, gy0 - (gy0 - gy1) * (broad + reveal * (prof - broad))))
    line(draw, canvas, broad_pts, rgba(COLORS["blue"], int(scene_alpha * 0.37)), 8)
    line(draw, canvas, sas_pts, rgba(COLORS["cyan"], scene_alpha), 4)
    # Lock point and moving laser cursor.
    lock_xn = 0.30
    scan = 0.48 * math.sin(local * 1.05) * math.exp(-max(local - 7, 0) * 0.42)
    cursor_xn = lock_xn + (1 - smooth((local - 6.0) / 4.5)) * (scan - lock_xn * 0.3)
    cursor = gx0 + (cursor_xn + 1) * 0.5 * (gx1 - gx0)
    lockpx = gx0 + (lock_xn + 1) * 0.5 * (gx1 - gx0)
    lock_alpha = int(scene_alpha * smooth((local - 4.2) / 1.0))
    line(draw, canvas, [(lockpx, gy1 + 12), (lockpx, gy0)], rgba(COLORS["green"], lock_alpha), 2)
    # The transient LOCK label fades before the persistent LOCKED badge enters.
    lock_text_alpha = int(lock_alpha * (1.0 - smooth((local - 9.2) / 0.8)))
    if local < 10.0:
        text(draw, canvas, (lockpx, 397), "LOCK", 17, COLORS["green"], "bold", "ms", lock_text_alpha)
    arrow(draw, canvas, (cursor, 708), (cursor, 665), COLORS["red"], 4, 13, scene_alpha)
    # Offset the equation from the vertical lock marker so no line crosses it.
    latex(im, canvas, "nu_laser", (cursor + 23, 731), 21, COLORS["red"], "lm", scene_alpha)
    if local > 10:
        pill(draw, canvas, (1434, 354), "LOCKED", COLORS["green"], int(scene_alpha * smooth((local - 10) / 1.4)), 192)
    # Bottom conceptual steps.
    a1 = int(scene_alpha * smooth((local - 3) / 1.0))
    a2 = int(scene_alpha * smooth((local - 6) / 1.0))
    a3 = int(scene_alpha * smooth((local - 9) / 1.0))
    pill(draw, canvas, (696, 887), "Doppler width", COLORS["blue"], a1, 230)
    text(draw, canvas, (946, 911), "→", 30, COLORS["muted"], "bold", "mm", a2)
    pill(draw, canvas, (980, 887), "narrow dip", COLORS["cyan"], a2, 218)
    text(draw, canvas, (1217, 911), "→", 30, COLORS["muted"], "bold", "mm", a3)
    pill(draw, canvas, (1252, 887), "stable frequency", COLORS["green"], a3, 292)
    return im


def gaussian_curve(mu, sigma, x):
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def draw_velocity_distribution(im, draw, canvas, u, alpha):
    panel(draw, canvas, (128, 355, 715, 817), alpha=190, radius=28)
    text(draw, canvas, (169, 394), "VELOCITY DISTRIBUTION", 17, COLORS["muted"], "bold", alpha=alpha)
    x0, x1, y0, y1 = 180, 662, 749, 450
    line(draw, canvas, [(x0, y1), (x0, y0), (x1, y0)], rgba(COLORS["line"], alpha), 2)
    latex(im, canvas, "velocity_axis", ((x0 + x1) / 2, 785), 22, COLORS["muted"], "mm", alpha)
    sigma = 0.86 * (1 - smooth(u)) + 0.19 * smooth(u)
    pts_hot, pts_now = [], []
    for i in range(181):
        x = -1.4 + 2.8 * i / 180
        xx = x0 + (x + 1.4) / 2.8 * (x1 - x0)
        hot = gaussian_curve(0, 0.86, x)
        now = gaussian_curve(0, sigma, x)
        pts_hot.append((xx, y0 - hot * (y0 - y1) * 0.82))
        pts_now.append((xx, y0 - now * (y0 - y1) * 0.82))
    line(draw, canvas, pts_hot, rgba(COLORS["red"], int(alpha * 0.35)), 5)
    line(draw, canvas, pts_now, rgba(COLORS["cyan"], alpha), 5)
    text(draw, canvas, (215, 493), "warm", 18, COLORS["red"], "bold", alpha=int(alpha * 0.7))
    text(draw, canvas, (516, 493), "cold", 18, COLORS["cyan"], "bold", alpha=alpha)
    # Velocity samples contract toward zero.
    rng = np.random.default_rng(912)
    raw = rng.normal(size=36)
    for i, q in enumerate(raw):
        vx = clamp(q * sigma / 1.4, -0.98, 0.98)
        xx = (x0 + x1) / 2 + vx * (x1 - x0) / 2
        yy = y0 + 18 + (i % 3) * 12
        draw.ellipse([canvas.p(xx - 3, yy - 3), canvas.p(xx + 3, yy + 3)], fill=rgba(COLORS["cyan"], int(alpha * 0.72)))


def draw_doppler(canvas: Canvas, t: float) -> Image.Image:
    im, draw = frame_shell(canvas, t)
    local = t - 23.0
    u = clamp(local / 19.0)
    scene_alpha = int(255 * smooth(min(local / 0.7, (19 - local) / 0.7)))
    section_title(draw, canvas, "02", "momentum transfer", "Light opposes motion", "Two beams red-detuned from resonance", scene_alpha)
    equation_badge(im, draw, canvas, (1374, 177, 1775, 241), "red_detuning", 27, COLORS["red"], scene_alpha)
    cool_u = smooth((local - 3.5) / 11.0)
    draw_velocity_distribution(im, draw, canvas, cool_u, scene_alpha)

    # One-dimensional optical molasses stage.
    panel(draw, canvas, (770, 333, 1788, 817), alpha=120, radius=30)
    cy = 564
    # Beam corridors.
    draw.rounded_rectangle([canvas.p(817, cy - 33), canvas.p(1737, cy + 33)], radius=canvas.s(31), fill=rgba(COLORS["red"], int(scene_alpha * 0.08)))
    for offset in (-18, 0, 18):
        arrow(draw, canvas, (827, cy + offset), (1115, cy + offset), COLORS["red"], 4, 16, int(scene_alpha * 0.8))
        arrow(draw, canvas, (1724, cy + offset), (1436, cy + offset), COLORS["cyan"], 4, 16, int(scene_alpha * 0.8))
    latex(im, canvas, "photon_red", (852, 477), 24, COLORS["red"], "lm", scene_alpha)
    latex(im, canvas, "photon_red", (1695, 477), 24, COLORS["cyan"], "rm", scene_alpha)
    # Atom initially moving right. The velocity arrow shrinks.
    atom_x = 1260 + 100 * (1 - math.exp(-2.0 * u))
    atom(draw, canvas, (atom_x, cy), 26, scene_alpha, COLORS["gold"])
    vlen = 220 * (1 - cool_u) + 24
    arrow(draw, canvas, (atom_x, cy - 92), (atom_x + vlen, cy - 92), COLORS["orange"], 6, 18, scene_alpha)
    text(draw, canvas, (atom_x + vlen / 2, cy - 127), "v", 28, COLORS["orange"], "bold", "mm", scene_alpha)
    # Preferential absorption from counterpropagating beam.
    event = pulse(local * 0.72)
    photon_x = 1635 - (260 * event)
    arrow(draw, canvas, (photon_x + 42, cy + 86), (photon_x, cy + 86), COLORS["cyan"], 4, 14, int(scene_alpha * 0.9))
    if event > 0.84:
        # Random spontaneous-emission directions; zero mean over many cycles.
        for j in range(7):
            a = j * 2 * math.pi / 7 + local * 0.4
            r = 36 + 35 * (event - 0.84) / 0.16
            line(draw, canvas, [(atom_x, cy), (atom_x + r * math.cos(a), cy + r * math.sin(a))], rgba(COLORS["violet"], int(scene_alpha * 0.55)), 2)
    text(draw, canvas, (1279, 721), "preferential absorption", 20, COLORS["cyan"], "bold", "mm", scene_alpha)
    text(draw, canvas, (1279, 751), "from the beam opposite to v", 18, COLORS["muted"], "regular", "mm", scene_alpha)

    # Key equation and physical floor.
    eq_alpha = int(scene_alpha * smooth((local - 6) / 1.0))
    panel(draw, canvas, (806, 858, 1290, 956), alpha=int(180 * eq_alpha / 255), radius=20)
    latex(im, canvas, "doppler_force", (1048, 906), 37, COLORS["white"], "mm", eq_alpha)
    panel(draw, canvas, (1322, 858, 1774, 956), alpha=int(180 * eq_alpha / 255), radius=20)
    text(draw, canvas, (1548, 892), "ideal Doppler limit", 16, COLORS["muted"], "bold", "mm", eq_alpha)
    latex(im, canvas, "doppler_temp", (1548, 928), 42, COLORS["cyan"], "mm", eq_alpha)
    return im


def draw_coils(draw, canvas, cx, cy, scale=1.0, alpha=255):
    # Anti-Helmholtz coil pair, viewed in perspective.
    for sign, y in ((1, cy - 230 * scale), (-1, cy + 230 * scale)):
        for k in range(5):
            pad = k * 9 * scale
            box = [canvas.p(cx - (255 + pad) * scale, y - (58 + pad * 0.2) * scale), canvas.p(cx + (255 + pad) * scale, y + (58 + pad * 0.2) * scale)]
            draw.ellipse(box, outline=rgba(COLORS["orange"], int(alpha * (0.78 - 0.07 * k))), width=canvas.s(5 * scale))
        # Direction arrow at one side.
        if sign > 0:
            arrow(draw, canvas, (cx - 190 * scale, y - 52 * scale), (cx - 75 * scale, y - 66 * scale), COLORS["gold"], 4, 16, alpha)
        else:
            arrow(draw, canvas, (cx - 75 * scale, y + 66 * scale), (cx - 190 * scale, y + 52 * scale), COLORS["gold"], 4, 16, alpha)


def draw_field_arrows(draw, canvas, cx, cy, alpha=255, width=760, height=430):
    for ix in range(-4, 5):
        for iy in range(-3, 4):
            if ix == 0 and iy == 0:
                continue
            x = cx + ix * width / 9
            y = cy + iy * height / 7
            bx = ix
            by = -2.0 * iy
            norm = math.hypot(bx, by)
            length = min(32, 6 + 4.2 * norm)
            ex = x + length * bx / norm
            ey = y + length * by / norm
            a = int(alpha * min(1.0, 0.35 + 0.12 * norm))
            arrow(draw, canvas, (x, y), (ex, ey), COLORS["violet"], 2.5, 8, a)


def draw_coil_scene(canvas: Canvas, t: float) -> Image.Image:
    im, draw = frame_shell(canvas, t)
    local = t - 42.0
    scene_alpha = int(255 * smooth(min(local / 0.7, (17 - local) / 0.7)))
    section_title(draw, canvas, "03", "quadrupole field", "The magnetic center is special", "Anti-Helmholtz coils: opposing currents and a field zero", scene_alpha)
    panel(draw, canvas, (142, 320, 1170, 875), alpha=105, radius=30)
    cx, cy = 655, 598
    coil_a = int(scene_alpha * smooth((local - 1.0) / 1.2))
    draw_coils(draw, canvas, cx, cy, 0.82, coil_a)
    draw_field_arrows(draw, canvas, cx, cy, int(coil_a * smooth((local - 2.5) / 1.2)), 670, 344)
    # Vacuum cell and magnetic zero.
    draw.rounded_rectangle([canvas.p(cx - 265, cy - 123), canvas.p(cx + 265, cy + 123)], radius=canvas.s(74), fill=(34, 87, 118, 24), outline=rgba(COLORS["cyan"], int(scene_alpha * 0.45)), width=canvas.s(2))
    for r, a in ((44, 18), (27, 42), (8, 255)):
        draw.ellipse([canvas.p(cx - r, cy - r), canvas.p(cx + r, cy + r)], fill=rgba(COLORS["green"], int(a * scene_alpha / 255)))
    text(draw, canvas, (cx, cy + 169), "field zero", 21, COLORS["green"], "bold", "mm", scene_alpha)
    text(draw, canvas, (cx, 849), "I", 24, COLORS["gold"], "bold", "mm", scene_alpha)
    # The Maxwell equation has a dedicated quiet zone, outside the field arrows.
    equation_badge(im, draw, canvas, (168, 344, 414, 407), "div_b", 27, COLORS["violet"], scene_alpha)

    # Concept card on the right.
    panel(draw, canvas, (1234, 321, 1780, 875), alpha=205, radius=30)
    text(draw, canvas, (1281, 367), "NEAR THE CENTER", 18, COLORS["muted"], "bold", alpha=scene_alpha)
    latex(im, canvas, "linear_field", (1281, 425), 43, COLORS["white"], "lm", scene_alpha)
    equation_badge(im, draw, canvas, (1280, 485, 1680, 537), "gradient_value", 24, COLORS["violet"], scene_alpha)
    # Zeeman ladder.
    y0 = 642
    for j, shift in enumerate((-58, 0, 58)):
        col = (COLORS["cyan"], COLORS["white"], COLORS["red"])[j]
        line(draw, canvas, [(1302, y0 + shift), (1492, y0 + shift)], rgba(col, scene_alpha), 4)
        latex(im, canvas, ("mf_minus", "mf_zero", "mf_plus")[j], (1518, y0 + shift), 20, col, "lm", scene_alpha)
    text(draw, canvas, (1281, 726), "The Zeeman shift changes", 21, COLORS["white"], "regular", alpha=scene_alpha)
    text(draw, canvas, (1281, 761), "which circular beam is closer to resonance.", 21, COLORS["white"], "regular", alpha=scene_alpha)
    text(draw, canvas, (1502, 811), "restoring force toward the center", 17, COLORS["green"], "bold", "mm", scene_alpha)
    arrow(draw, canvas, (1304, 846), (1699, 846), COLORS["green"], 5, 17, scene_alpha)
    return im


def precompute_mot_particles(fps: int, seconds: float, count: int = 440, seed: int = 2026):
    """Integrate a scaled Langevin model for a captured atomic subensemble."""
    frames = int(math.ceil(seconds * fps)) + 2
    rng = np.random.default_rng(seed)
    pos = rng.uniform(-1.0, 1.0, size=(count, 2)).astype(np.float32)
    pos[:, 1] *= 0.72
    vel = rng.normal(0, 0.55, size=(count, 2)).astype(np.float32)
    # A few atoms enter from the edges like a vapor-cell loading process.
    pos[: count // 4, 0] = rng.choice((-1.2, 1.2), size=count // 4)
    vel[: count // 4, 0] = -np.sign(pos[: count // 4, 0]) * rng.uniform(0.2, 0.85, count // 4)
    positions = np.empty((frames, count, 2), dtype=np.float32)
    velocities = np.empty_like(positions)
    brightness = rng.uniform(0.58, 1.0, count).astype(np.float32)
    phase = rng.uniform(0, 2 * math.pi, count).astype(np.float32)
    dt = 1.0 / fps
    for k in range(frames):
        u = k / max(frames - 1, 1)
        ramp = smooth((u - 0.10) / 0.31)
        gamma = 0.08 + 2.10 * ramp
        spring = 0.02 + 2.85 * ramp
        diffusion = 0.22 * (1 - ramp) + 0.055
        noise = rng.normal(size=(count, 2)).astype(np.float32)
        # Damped harmonic MOT force plus recoil diffusion.
        vel += (-gamma * vel - spring * pos) * dt + diffusion * math.sqrt(dt) * noise
        pos += vel * dt
        # Small 3D-projection breathing term; not part of the force integration.
        positions[k] = pos
        velocities[k] = vel
    return positions, velocities, brightness, phase


def draw_beam(draw, canvas, a, b, color, alpha=90, width=52, arrows=True):
    line(draw, canvas, [a, b], rgba(color, int(alpha * 0.22)), width)
    line(draw, canvas, [a, b], rgba(color, int(alpha * 0.62)), max(2, width // 7))
    if arrows:
        qx = a[0] * 0.58 + b[0] * 0.42
        qy = a[1] * 0.58 + b[1] * 0.42
        rx = a[0] * 0.42 + b[0] * 0.58
        ry = a[1] * 0.42 + b[1] * 0.58
        arrow(draw, canvas, (qx, qy), (rx, ry), color, 4, 15, min(255, alpha * 2))


def draw_mot_scene(canvas: Canvas, t: float, particle_data, fps: int) -> Image.Image:
    im, draw = frame_shell(canvas, t)
    local = t - 59.0
    u = clamp(local / 25.0)
    scene_alpha = int(255 * smooth(min(local / 0.7, (25 - local) / 0.7)))
    section_title(draw, canvas, "04", "light + field", "Now the trap appears", "Six beams, two coils and a restoring force in 3D", scene_alpha)
    panel(draw, canvas, (102, 304, 1325, 919), alpha=90, radius=34)
    cx, cy = 705, 614
    # Back beams first for pseudo-depth.
    draw_beam(draw, canvas, (299, 855), (1090, 375), COLORS["violet"], int(scene_alpha * 0.62), 48)
    draw_beam(draw, canvas, (1090, 375), (299, 855), COLORS["magenta"], int(scene_alpha * 0.62), 48)
    draw_beam(draw, canvas, (705, 326), (705, 902), COLORS["cyan"], int(scene_alpha * 0.63), 56)
    draw_beam(draw, canvas, (705, 902), (705, 326), COLORS["blue"], int(scene_alpha * 0.63), 56)
    draw_beam(draw, canvas, (152, 614), (1256, 614), COLORS["red"], int(scene_alpha * 0.63), 56)
    draw_beam(draw, canvas, (1256, 614), (152, 614), COLORS["cyan"], int(scene_alpha * 0.63), 56)
    draw_coils(draw, canvas, cx, cy, 0.54, int(scene_alpha * 0.55))
    # Glass chamber.
    draw.rounded_rectangle([canvas.p(cx - 322, cy - 190), canvas.p(cx + 322, cy + 190)], radius=canvas.s(104), fill=(30, 87, 120, 20), outline=rgba(COLORS["cyan"], int(scene_alpha * 0.36)), width=canvas.s(2))
    line(draw, canvas, [(cx - 274, cy - 165), (cx + 250, cy - 165)], rgba(COLORS["white"], int(scene_alpha * 0.18)), 2)

    positions, velocities, brightness, phase = particle_data
    idx = min(int(local * fps), positions.shape[0] - 1)
    p = positions[idx]
    # Particles farther from center are dimmer: capture region is finite.
    rad = np.linalg.norm(p, axis=1)
    for i in np.argsort(rad)[::-1]:
        x = cx + 390 * p[i, 0]
        y = cy + 310 * p[i, 1] + 6 * math.sin(phase[i] + local * 0.6)
        if not (160 < x < 1250 and 355 < y < 885):
            continue
        a = int(scene_alpha * brightness[i] * clamp(1.15 - 0.28 * rad[i]))
        rr = 1.5 + 1.8 * clamp(1.0 - rad[i] / 1.4)
        atom(draw, canvas, (x, y), rr, a, COLORS["gold"])
    # Central cloud glow grows as position variance contracts.
    cloud = smooth((u - 0.36) / 0.5)
    if cloud > 0:
        glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        for r, a in ((94, 10), (62, 19), (32, 38), (12, 110)):
            gd.ellipse([canvas.p(cx - r, cy - r * 0.72), canvas.p(cx + r, cy + r * 0.72)], fill=rgba(COLORS["gold"], int(a * cloud * scene_alpha / 255)))
        glow = glow.filter(ImageFilter.GaussianBlur(canvas.s(13)))
        im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
        draw = ImageDraw.Draw(im, "RGBA")

    # Side diagnostic card.
    panel(draw, canvas, (1372, 304, 1806, 919), alpha=205, radius=30)
    text(draw, canvas, (1412, 350), "MOT INGREDIENTS", 18, COLORS["muted"], "bold", alpha=scene_alpha)
    items = (
        ("mot_detuning", "red-detuned laser", COLORS["red"], True),
        ("repumper ON", "prevents a dark F = 1 state", COLORS["cyan"], False),
        ("gradient_value", "gradient", COLORS["violet"], True),
    )
    for j, (value, label, col, is_equation) in enumerate(items):
        yy = 425 + j * 112
        draw.ellipse([canvas.p(1410, yy - 8), canvas.p(1426, yy + 8)], fill=rgba(col, scene_alpha))
        if is_equation:
            latex(im, canvas, value, (1452, yy - 3), 27, COLORS["white"], "lm", scene_alpha)
        else:
            text(draw, canvas, (1452, yy - 16), value, 27, COLORS["white"], "bold", alpha=scene_alpha)
        text(draw, canvas, (1452, yy + 22), label, 18, COLORS["muted"], "regular", alpha=scene_alpha)
    line(draw, canvas, [(1412, 741), (1765, 741)], rgba(COLORS["line"], int(scene_alpha * 0.75)), 1)
    latex(im, canvas, "mot_force", (1588, 794), 29, COLORS["green"], "mm", scene_alpha)
    text(draw, canvas, (1588, 838), "cooling + restoring force", 18, COLORS["muted"], "regular", "mm", scene_alpha)
    # Compression meter from simulated ensemble.
    sigma_r = float(np.sqrt(np.mean(np.sum(p * p, axis=1))))
    frac = clamp(1.0 - sigma_r / 0.95)
    draw.rounded_rectangle([canvas.p(1413, 876), canvas.p(1765, 891)], radius=canvas.s(8), fill=rgba(COLORS["line"], int(scene_alpha * 0.6)))
    draw.rounded_rectangle([canvas.p(1413, 876), canvas.p(1413 + 352 * frac, 891)], radius=canvas.s(8), fill=rgba(COLORS["green"], scene_alpha))
    return im


def draw_final(canvas: Canvas, t: float, particle_data, fps: int) -> Image.Image:
    im, draw = frame_shell(canvas, t)
    local = t - 84.0
    u = clamp(local / 14.0)
    scene_alpha = int(255 * smooth(min(local / 0.7, (14 - local) / 1.0 if local > 12.6 else 1)))
    text(draw, canvas, (960, 118), "RESULT", 22, COLORS["cyan"], "bold", "mm", scene_alpha)
    text(draw, canvas, (960, 180), "A cold, localized, fluorescent cloud", 53, COLORS["white"], "bold", "mm", scene_alpha)
    text(draw, canvas, (960, 231), "Only the slow fraction of the vapor is captured", 24, COLORS["muted"], "regular", "mm", scene_alpha)
    cx, cy = 960, 579
    # Dark viewing chamber and faint beams.
    draw.rounded_rectangle([canvas.p(298, 309), canvas.p(1622, 840)], radius=canvas.s(86), fill=(3, 8, 19, int(scene_alpha * 0.62)), outline=rgba(COLORS["line"], int(scene_alpha * 0.65)), width=canvas.s(2))
    draw_beam(draw, canvas, (350, cy), (1570, cy), COLORS["red"], int(scene_alpha * 0.20), 76, False)
    draw_beam(draw, canvas, (cx, 345), (cx, 811), COLORS["cyan"], int(scene_alpha * 0.18), 72, False)
    draw_beam(draw, canvas, (560, 790), (1360, 370), COLORS["violet"], int(scene_alpha * 0.17), 62, False)

    # Beauty cloud with deterministic flicker and many points.
    rng = np.random.default_rng(881)
    count = 760
    pts = rng.normal(size=(count, 2))
    pts[:, 0] *= 58
    pts[:, 1] *= 37
    radial = np.sqrt((pts[:, 0] / 58) ** 2 + (pts[:, 1] / 37) ** 2)
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    breathe = 1 + 0.025 * math.sin(local * 1.3)
    for r, a in ((150, 7), (104, 15), (65, 34), (28, 82)):
        gd.ellipse([canvas.p(cx - r * breathe, cy - r * 0.64 * breathe), canvas.p(cx + r * breathe, cy + r * 0.64 * breathe)], fill=rgba(COLORS["gold"], int(a * scene_alpha / 255)))
    glow = glow.filter(ImageFilter.GaussianBlur(canvas.s(24)))
    im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(im, "RGBA")
    for i in np.argsort(radial)[::-1]:
        if radial[i] > 3.0:
            continue
        x = cx + pts[i, 0] * breathe
        y = cy + pts[i, 1] * breathe
        flicker = 0.76 + 0.24 * math.sin(i * 2.17 + local * (1.2 + i % 7 * 0.03))
        a = int(scene_alpha * flicker * clamp(1.1 - radial[i] / 3.1))
        atom(draw, canvas, (x, y), 1.2 + 1.8 * clamp(1 - radial[i] / 2.6), a, COLORS["gold"])
    atom(draw, canvas, (cx, cy), 8, scene_alpha, COLORS["white"])
    # Callouts.
    call_alpha = int(scene_alpha * smooth((local - 2.0) / 1.6))
    line(draw, canvas, [(894, 543), (668, 414), (478, 414)], rgba(COLORS["cyan"], call_alpha), 2)
    text(draw, canvas, (467, 393), "millimeter scale", 22, COLORS["cyan"], "bold", "ra", call_alpha)
    latex(im, canvas, "cloud_size", (467, 433), 19, COLORS["muted"], "rm", call_alpha)
    text(draw, canvas, (467, 458), "typical value", 15, COLORS["muted"], "regular", "ra", call_alpha)
    line(draw, canvas, [(1018, 548), (1257, 411), (1451, 411)], rgba(COLORS["violet"], call_alpha), 2)
    text(draw, canvas, (1463, 390), "Doppler-scale temperature", 22, COLORS["violet"], "bold", alpha=call_alpha)
    latex(im, canvas, "cloud_temp", (1463, 433), 19, COLORS["muted"], "lm", call_alpha)
    line(draw, canvas, [(1012, 614), (1270, 743), (1451, 743)], rgba(COLORS["gold"], call_alpha), 2)
    text(draw, canvas, (1463, 722), "fluorescence at 780 nm", 22, COLORS["gold"], "bold", alpha=call_alpha)
    text(draw, canvas, (1463, 757), "color enhanced for visibility", 18, COLORS["muted"], "regular", alpha=call_alpha)

    # Final synthesis ribbon.
    recap_alpha = int(scene_alpha * smooth((local - 6.0) / 1.3))
    y = 899
    labels = (("SAS", COLORS["cyan"], None), (None, COLORS["red"], "delta_negative"), (None, COLORS["violet"], "grad_b"), ("MOT", COLORS["green"], None))
    xs = (544, 804, 1064, 1324)
    for j, ((label, col, equation_key), x) in enumerate(zip(labels, xs)):
        if equation_key:
            draw.rounded_rectangle([canvas.p(x - 85, y - 26), canvas.p(x + 85, y + 22)], radius=canvas.s(24), fill=rgba(col, int(recap_alpha * 0.16)), outline=rgba(col, int(recap_alpha * 0.62)), width=canvas.s(1.5))
            latex(im, canvas, equation_key, (x, y - 2), 24, col, "mm", recap_alpha)
        else:
            pill(draw, canvas, (x - 85, y - 26), label, col, recap_alpha, 170)
        if j < len(labels) - 1:
            text(draw, canvas, (x + 111, y - 1), "+" if j < 2 else "→", 29, COLORS["muted"], "bold", "mm", recap_alpha)
    # Final quantitative card. It deliberately replaces (rather than overlays)
    # the cloud annotations, keeping every equation in its own quiet zone.
    numbers_u = smooth((local - 8.0) / 1.1)
    if numbers_u > 0:
        numbers_alpha = int(scene_alpha * numbers_u)
        draw.rectangle(
            [canvas.p(0, 0), canvas.p(DESIGN_W, 968)],
            fill=rgba(COLORS["bg0"], int(255 * numbers_u)),
        )
        text(draw, canvas, (960, 112), "EXPERIMENTAL SCALES", 21, COLORS["cyan"], "bold", "mm", numbers_alpha)
        text(draw, canvas, (960, 176), "What does “real time” mean?", 51, COLORS["white"], "bold", "mm", numbers_alpha)
        text(draw, canvas, (960, 226), "A representative ⁸⁷Rb vapor-cell MOT example", 23, COLORS["muted"], "regular", "mm", numbers_alpha)

        equation_badge(
            im,
            draw,
            canvas,
            (432, 272, 1488, 374),
            "loading_model",
            52,
            COLORS["white"],
            numbers_alpha,
        )

        metrics = (
            ((220, 430, 690, 753), "COOLING", "cooling_time", "slowing a captured atom", COLORS["cyan"]),
            ((725, 430, 1195, 753), "MOT LOADING", "loading_time", "toward the steady-state population", COLORS["violet"]),
            ((1230, 430, 1700, 753), "TYPICAL POPULATION", "atom_number", "about 50 million atoms", COLORS["gold"]),
        )
        for box, label, equation_key, note, col in metrics:
            x0, y0, x1, y1 = box
            panel(draw, canvas, box, alpha=int(205 * numbers_u), radius=28)
            draw.ellipse([canvas.p(x0 + 35, y0 + 37), canvas.p(x0 + 51, y0 + 53)], fill=rgba(col, numbers_alpha))
            text(draw, canvas, (x0 + 72, y0 + 32), label, 18, COLORS["muted"], "bold", alpha=numbers_alpha)
            latex(im, canvas, equation_key, ((x0 + x1) / 2, y0 + 151), 37, col, "mm", numbers_alpha)
            line(draw, canvas, [(x0 + 38, y0 + 209), (x1 - 38, y0 + 209)], rgba(COLORS["line"], int(numbers_alpha * 0.70)), 1)
            text(draw, canvas, ((x0 + x1) / 2, y0 + 257), note, 19, COLORS["white"], "regular", "mm", numbers_alpha)

        text(draw, canvas, (960, 819), "Order of magnitude, not a universal specification", 20, COLORS["green"], "bold", "mm", numbers_alpha)
        text(
            draw,
            canvas,
            (960, 860),
            "Depends on beam power and diameter, Rb pressure, and collisional losses.",
            20,
            COLORS["muted"],
            "regular",
            "mm",
            numbers_alpha,
        )
    elif local > 10.2:
        text(draw, canvas, (960, 972), "Atomic physics made visible, in real time", 21, COLORS["white"], "bold", "mm", int(scene_alpha * smooth((local - 10.2) / 1.0)))
    return im


def render_frame(canvas: Canvas, t: float, particle_data, fps: int) -> Image.Image:
    if t < 6:
        im = draw_intro(canvas, t)
    elif t < 23:
        im = draw_sas(canvas, t)
    elif t < 42:
        im = draw_doppler(canvas, t)
    elif t < 59:
        im = draw_coil_scene(canvas, t)
    elif t < 84:
        im = draw_mot_scene(canvas, t, particle_data, fps)
    else:
        im = draw_final(canvas, t, particle_data, fps)
    # Very short cinematic fades.
    draw = ImageDraw.Draw(im, "RGBA")
    if t < 0.8:
        a = int(255 * (1 - smooth(t / 0.8)))
        draw.rectangle([0, 0, canvas.width, canvas.height], fill=(0, 0, 0, a))
    if t > TOTAL_DURATION - 1.0:
        a = int(255 * smooth((t - (TOTAL_DURATION - 1.0)) / 1.0))
        draw.rectangle([0, 0, canvas.width, canvas.height], fill=(0, 0, 0, a))
    return im.convert("RGB")


def synth_audio(path: Path, duration: float, sample_rate: int = 44100):
    """Create an original, restrained ambient underscore with scene cues."""
    n = int(duration * sample_rate)
    tt = np.arange(n, dtype=np.float64) / sample_rate
    audio = np.zeros(n, dtype=np.float64)
    chords = (
        (0, 23, (55.00, 82.41, 110.00, 164.81)),
        (23, 42, (48.99, 73.42, 98.00, 146.83)),
        (42, 59, (61.74, 92.50, 123.47, 185.00)),
        (59, 84, (55.00, 82.41, 123.47, 164.81)),
        (84, 98, (65.41, 98.00, 130.81, 196.00)),
    )
    for start, end, freqs in chords:
        mask = (tt >= start) & (tt < end)
        local = tt[mask] - start
        segdur = end - start
        env = np.minimum(1, local / 2.2) * np.minimum(1, (segdur - local) / 2.2)
        pad = np.zeros_like(local)
        for j, f in enumerate(freqs):
            vibrato = 0.35 * np.sin(2 * np.pi * (0.035 + 0.007 * j) * local + j)
            phase = 2 * np.pi * f * local + vibrato
            pad += (0.55 / (j + 1) ** 0.45) * np.sin(phase)
            pad += (0.08 / (j + 1)) * np.sin(2 * phase + 0.7)
        shimmer = 0.05 * np.sin(2 * np.pi * freqs[-1] * 2 * local + 0.8 * np.sin(2 * np.pi * 0.06 * local))
        audio[mask] += env * (pad + shimmer)
    # Soft pings at conceptual transitions.
    for cue, base in ((6, 392.0), (23, 329.63), (42, 440.0), (59, 523.25), (84, 659.25), (92, 783.99)):
        idx = tt >= cue
        local = tt[idx] - cue
        env = np.exp(-local * 1.75)
        ping = np.sin(2 * np.pi * base * local) + 0.42 * np.sin(2 * np.pi * base * 2.01 * local)
        audio[idx] += 0.20 * env * ping
    # A quiet photon-like tick texture in the cooling/capture sections.
    rng = np.random.default_rng(78024)
    for cue in np.arange(25.0, 82.0, 1.15):
        cue += rng.uniform(-0.18, 0.18)
        start = int(cue * sample_rate)
        length = min(int(0.09 * sample_rate), n - start)
        if length <= 0:
            continue
        local = np.arange(length) / sample_rate
        tick = 0.025 * np.exp(-local * 55) * np.sin(2 * np.pi * rng.uniform(1200, 2200) * local)
        audio[start : start + length] += tick
    # Slow master envelope, conservative level for a narrated workshop.
    master = np.minimum(1, tt / 2.5) * np.minimum(1, (duration - tt) / 3.0)
    audio *= master
    peak = max(np.max(np.abs(audio)), 1e-9)
    audio = 0.30 * audio / peak
    stereo = np.column_stack((audio, audio * 0.97))
    pcm = np.int16(np.clip(stereo, -1, 1) * 32767)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm.tobytes())


def encode_video(args):
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    silent = output.with_name(output.stem + "_silent.mp4")
    audio = output.with_name(output.stem + "_score.wav")
    canvas = Canvas(args.width, args.height)
    particle_data = precompute_mot_particles(args.fps, 25.0)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    frame_count = int(math.ceil((args.end - args.start) * args.fps))
    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s:v",
        f"{args.width}x{args.height}",
        "-r",
        str(args.fps),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        args.preset,
        "-crf",
        str(args.crf),
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(silent),
    ]
    print(f"Rendering {frame_count} frames at {args.width}x{args.height}/{args.fps} fps…", flush=True)
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for k in range(frame_count):
            t = args.start + k / args.fps
            frame = render_frame(canvas, t, particle_data, args.fps)
            proc.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())
            if k % max(args.fps * 3, 1) == 0 or k == frame_count - 1:
                print(f"  {k + 1:4d}/{frame_count}  t={t:5.1f} s", flush=True)
    finally:
        proc.stdin.close()
    code = proc.wait()
    if code != 0:
        raise RuntimeError(f"ffmpeg video encoding failed with exit code {code}")

    if args.no_audio:
        if output.exists():
            output.unlink()
        silent.replace(output)
    else:
        segment_duration = args.end - args.start
        synth_audio(audio, segment_duration)
        mux = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(silent),
            "-i",
            str(audio),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(output),
        ]
        subprocess.run(mux, check=True)
        silent.unlink(missing_ok=True)
        if not args.keep_audio:
            audio.unlink(missing_ok=True)
    print(f"Done: {output}", flush=True)


def render_stills(args):
    outdir = Path(args.stills).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(args.width, args.height)
    particle_data = precompute_mot_particles(args.fps, 25.0)
    times = args.times or [3.0, 15.0, 32.0, 51.0, 72.0, 90.0]
    for t in times:
        frame = render_frame(canvas, t, particle_data, args.fps)
        path = outdir / f"frame_{t:05.1f}s.png"
        frame.save(path, quality=95)
        print(path)


def build_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", default="MOT_Rb87_workshop_1080p.mp4")
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--start", type=float, default=0.0)
    p.add_argument("--end", type=float, default=TOTAL_DURATION)
    p.add_argument("--crf", type=int, default=17)
    p.add_argument("--preset", default="medium")
    p.add_argument("--no-audio", action="store_true")
    p.add_argument("--keep-audio", action="store_true")
    p.add_argument("--stills", help="Render key PNG frames to this directory instead of a video.")
    p.add_argument("--times", type=float, nargs="*", help="Times for --stills.")
    return p


def main():
    args = build_parser().parse_args()
    if args.width * 9 != args.height * 16:
        raise SystemExit("Width and height must have a 16:9 ratio.")
    if not (0 <= args.start < args.end <= TOTAL_DURATION):
        raise SystemExit(f"Require 0 <= start < end <= {TOTAL_DURATION}.")
    if args.stills:
        render_stills(args)
    else:
        encode_video(args)


if __name__ == "__main__":
    main()
