"""
Fullscreen three-body screensaver using pygame.

Run:  python fullscreen_saver.py [--config path/to/config.toml]
Exit: press any key, move mouse, or click.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from collections import deque
from pathlib import Path

import pygame

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


DEFAULT_CONFIG = Path(__file__).parent / "config.toml"


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    """Convert '82A0BE' or '#82A0BE' to (130, 160, 190)."""
    h = h.lstrip("#")
    return (
        int(h[0:2], 16),
        int(h[2:4], 16),
        int(h[4:6], 16),
    )


def _parse_color(val: str | list) -> tuple[int, int, int]:
    if isinstance(val, str):
        return _hex_to_rgb(val)
    return (int(val[0]), int(val[1]), int(val[2]))


def _load_config(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


# ── Star / physics ───────────────────────────────────────────────


class _Star:
    __slots__ = (
        "mass", "radius", "x", "y",
        "vx", "vy", "tail", "color",
    )

    def __init__(
        self, mass: float, pos: list, vel: list,
        color: str | list, tail_len: int,
    ) -> None:
        self.mass = float(mass)
        self.radius = float(mass ** (1.0 / 3.0))
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.vx = float(vel[0])
        self.vy = float(vel[1])
        self.color = _parse_color(color)
        self.tail: deque[tuple[float, float]] = deque(
            maxlen=tail_len,
        )
        self.tail.append((self.x, self.y))


def _build_stars(cfg: dict) -> list[_Star]:
    tail_len = cfg["display"]["tail_length"]
    stars = [
        _Star(
            s["mass"], s["position"], s["velocity"],
            s["color"], tail_len,
        )
        for s in cfg["stars"]
    ]
    # Shift into center-of-mass rest frame
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


def _step(
    stars: list[_Star], dt: float, g: float,
) -> None:
    """One velocity-Verlet integration step."""
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


def _to_screen(
    x: float, y: float,
    scale: float, ox: float, oy: float,
) -> tuple[float, float]:
    """Simulation coords to screen coords."""
    return x * scale + ox, -y * scale + oy


# ── Main loop ────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Three-body screensaver",
    )
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG,
        help="Path to TOML config file",
    )
    args = parser.parse_args()
    cfg = _load_config(args.config)

    # Read config sections
    phys = cfg["physics"]
    disp = cfg["display"]
    zoom_cfg = cfg.get("zoom", {})

    g = float(phys["G"])
    dt = float(phys["dt"])
    steps = int(phys["steps_per_frame"])
    fps = int(disp["fps"])
    bg = _parse_color(disp["background"])
    star_sc = float(disp.get("star_scale", 0.15))
    star_min = float(disp.get("star_min_size", 3))
    star_max = float(disp.get("star_max_size", 30))

    zoom_margin = float(zoom_cfg.get("margin", 1.3))
    damping = float(zoom_cfg.get("damping", 0.03))
    min_scale = float(zoom_cfg.get("min_scale", 1.0))
    max_scale = float(zoom_cfg.get("max_scale", 50.0))

    # Init pygame with vsync
    os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
    os.environ["SDL_RENDER_VSYNC"] = "1"
    pygame.init()
    screen = pygame.display.set_mode(
        (0, 0),
        pygame.FULLSCREEN | pygame.NOFRAME
        | pygame.DOUBLEBUF | pygame.HWSURFACE,
    )
    w, h = screen.get_size()
    pygame.display.set_caption("")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    stars = _build_stars(cfg)

    # Init smooth zoom tracking
    xs = [s.x for s in stars]
    ys = [s.y for s in stars]
    span = max(
        max(xs) - min(xs), max(ys) - min(ys), 10.0,
    )
    smooth_scale = min(w, h) / (span * zoom_margin)
    smooth_scale = max(min_scale, min(max_scale, smooth_scale))
    smooth_ox = w / 2.0
    smooth_oy = h / 2.0

    pygame.event.clear()
    pygame.mouse.get_rel()

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type in (pygame.QUIT, pygame.KEYDOWN,
                           pygame.MOUSEBUTTONDOWN):
                running = False
            elif ev.type == pygame.MOUSEMOTION:
                if abs(ev.rel[0]) > 5 or abs(ev.rel[1]) > 5:
                    running = False

        # Physics
        for _ in range(steps):
            _step(stars, dt, g)

        # Auto-zoom with damping
        xs = [s.x for s in stars]
        ys = [s.y for s in stars]
        cx = (max(xs) + min(xs)) / 2.0
        cy = (max(ys) + min(ys)) / 2.0
        span = max(
            max(xs) - min(xs), max(ys) - min(ys), 10.0,
        )
        half_sim = span / 2.0 * zoom_margin
        t_scale = min(w, h) / (half_sim * 2.0)
        t_scale = max(min_scale, min(max_scale, t_scale))
        t_ox = w / 2.0 - cx * t_scale
        t_oy = h / 2.0 + cy * t_scale

        smooth_scale += (t_scale - smooth_scale) * damping
        smooth_ox += (t_ox - smooth_ox) * damping
        smooth_oy += (t_oy - smooth_oy) * damping

        scale = smooth_scale
        ox = smooth_ox
        oy = smooth_oy

        # Render
        screen.fill(bg)

        # Tails first
        for star in stars:
            tail = list(star.tail)
            if len(tail) > 1:
                pts = [
                    _to_screen(p[0], p[1], scale, ox, oy)
                    for p in tail
                ]
                pygame.draw.aalines(
                    screen, star.color, False, pts,
                )

        # Stars on top
        for star in stars:
            sx, sy = _to_screen(
                star.x, star.y, scale, ox, oy,
            )
            sz = star.radius * scale * star_sc
            sz = max(star_min, min(star_max, sz))
            pygame.draw.circle(
                screen, star.color, (sx, sy), sz,
            )

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
