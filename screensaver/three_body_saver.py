"""
macOS native screen saver — Three-Body gravitational simulation.

Built with pyobjc, packaged as a .saver bundle via py2app.
Reads config from config.toml next to this file.
"""

import math
from collections import deque
from pathlib import Path

import objc
from AppKit import NSBezierPath, NSColor
from ScreenSaver import ScreenSaverView

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

_CFG_PATH = Path(__file__).parent / "config.toml"


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (
        int(h[0:2], 16),
        int(h[2:4], 16),
        int(h[4:6], 16),
    )


def _parse_color(val):
    if isinstance(val, str):
        return _hex_to_rgb(val)
    return (int(val[0]), int(val[1]), int(val[2]))


def _load_config() -> dict:
    with open(_CFG_PATH, "rb") as f:
        return tomllib.load(f)


# ── Star / physics ───────────────────────────────────────────────


class _Star:
    __slots__ = (
        "mass", "radius", "x", "y",
        "vx", "vy", "tail", "color",
    )

    def __init__(self, mass, pos, vel, color, tail_len):
        self.mass = float(mass)
        self.radius = float(mass ** (1.0 / 3.0))
        self.x, self.y = float(pos[0]), float(pos[1])
        self.vx, self.vy = float(vel[0]), float(vel[1])
        rgb = _parse_color(color)
        self.color = tuple(c / 255.0 for c in rgb)
        self.tail = deque(maxlen=tail_len)
        self.tail.append((self.x, self.y))


def _build_stars(cfg: dict) -> list:
    tail_len = cfg["display"]["tail_length"]
    stars = [
        _Star(
            s["mass"], s["position"], s["velocity"],
            s["color"], tail_len,
        )
        for s in cfg["stars"]
    ]
    tm = sum(s.mass for s in stars)
    px = sum(s.mass * s.vx for s in stars)
    py = sum(s.mass * s.vy for s in stars)
    cx = sum(s.mass * s.x for s in stars) / tm
    cy = sum(s.mass * s.y for s in stars) / tm
    for s in stars:
        s.vx -= px / tm
        s.vy -= py / tm
        s.x -= cx
        s.y -= cy
        s.tail.clear()
        s.tail.append((s.x, s.y))
    return stars


def _step(stars, dt, g):
    n = len(stars)
    ax = [0.0] * n
    ay = [0.0] * n
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dx = stars[i].x - stars[j].x
            dy = stars[i].y - stars[j].y
            r = math.sqrt(dx * dx + dy * dy)
            if r < 0.01:
                continue
            f = g * stars[j].mass / r
            ax[i] -= (dx / r) * f
            ay[i] -= (dy / r) * f
    for i, s in enumerate(stars):
        hx = 0.5 * dt * ax[i]
        hy = 0.5 * dt * ay[i]
        s.vx += hx
        s.vy += hy
        s.x += s.vx * dt
        s.y += s.vy * dt
        s.vx += hx
        s.vy += hy
        s.tail.append((s.x, s.y))


# ── ScreenSaverView ──────────────────────────────────────────────


class ThreeBodySaver(ScreenSaverView):
    """macOS ScreenSaverView rendering the three-body sim."""

    def initWithFrame_isPreview_(self, frame, preview):
        self = objc.super(
            ThreeBodySaver, self,
        ).initWithFrame_isPreview_(frame, preview)
        if self is None:
            return None

        cfg = _load_config()
        phys = cfg["physics"]
        disp = cfg["display"]

        self._g = float(phys["G"])
        self._dt = float(phys["dt"])
        self._steps = int(phys["steps_per_frame"])
        self._tail_thick = float(disp.get("tail_thickness", 1.5))
        self._star_sc = float(disp.get("star_scale", 0.15))
        self._star_min = float(disp.get("star_min_size", 3))
        self._star_max = float(disp.get("star_max_size", 30))

        bg_rgb = _parse_color(disp["background"])
        self._bg = tuple(c / 255.0 for c in bg_rgb)

        self.setAnimationTimeInterval_(1.0 / int(disp["fps"]))
        self._stars = _build_stars(cfg)
        return self

    def animateOneFrame(self):
        bounds = self.bounds()
        w = bounds.size.width
        h = bounds.size.height

        # Background
        br, bg, bb = self._bg
        NSColor.colorWithCalibratedRed_green_blue_alpha_(
            br, bg, bb, 1.0,
        ).set()
        NSBezierPath.fillRect_(bounds)

        scale = min(w, h) / 160.0
        ox, oy = w / 2.0, h / 2.0

        for _ in range(self._steps):
            _step(self._stars, self._dt, self._g)

        # Tails first
        for star in self._stars:
            sr, sg, sb = star.color
            tail = list(star.tail)
            if len(tail) > 1:
                for i in range(1, len(tail)):
                    frac = i / len(tail)
                    alpha = frac * 0.8
                    NSColor.colorWithCalibratedRed_green_blue_alpha_(
                        sr, sg, sb, alpha,
                    ).set()
                    path = NSBezierPath.bezierPath()
                    x0 = tail[i - 1][0] * scale + ox
                    y0 = tail[i - 1][1] * scale + oy
                    x1 = tail[i][0] * scale + ox
                    y1 = tail[i][1] * scale + oy
                    path.moveToPoint_((x0, y0))
                    path.lineToPoint_((x1, y1))
                    path.setLineWidth_(self._tail_thick)
                    path.stroke()

        # Stars on top
        for star in self._stars:
            sr, sg, sb = star.color
            sx = star.x * scale + ox
            sy = star.y * scale + oy
            sz = star.radius * scale * self._star_sc
            sz = max(self._star_min, min(self._star_max, sz))
            NSColor.colorWithCalibratedRed_green_blue_alpha_(
                sr, sg, sb, 1.0,
            ).set()
            NSBezierPath.bezierPathWithOvalInRect_(
                ((sx - sz, sy - sz), (sz * 2, sz * 2)),
            ).fill()

    def hasConfigureSheet(self):
        return False

    def configureSheet(self):
        return None


objc.removeAutoreleasePool()
