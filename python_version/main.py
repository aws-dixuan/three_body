"""Three-body (N-body) gravitational simulation.

Run:
    python main.py            # 2D view
    python main.py --3d       # 3D view
"""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

try:
    from python_version.star import Star
    from python_version.system import System
except ImportError:
    from star import Star
    from system import System

DT = 0.1
TAIL_LENGTH = 200
INTERVAL_MS = 10
MARGIN = 1.3


def build_default_system() -> System:
    """Create the default three-body scenario."""
    stars = [
        Star(
            mass=100.0,
            position=[10.0, 10.0, 7.0],
            velocity=[-4.0, -3.4, 10.0],
            tail_length=TAIL_LENGTH,
        ),
        Star(
            mass=100.5,
            position=[-10.0, -10.0, 7.0],
            velocity=[2.3, -0.9, -3.0],
            tail_length=TAIL_LENGTH,
        ),
        Star(
            mass=130.2,
            position=[10.0, -10.0, -3.0],
            velocity=[2.2, 1.8, 8.0],
            tail_length=TAIL_LENGTH,
        ),
    ]
    return System(stars, dt=DT)


# ── Drawing ──────────────────────────────────────────────────────


def _auto_zoom_2d(
    ax: plt.Axes, system: System,
) -> None:
    """Set axis limits to keep all stars in view."""
    xs = [s.position[0] for s in system.stars]
    ys = [s.position[1] for s in system.stars]
    cx = (max(xs) + min(xs)) / 2.0
    cy = (max(ys) + min(ys)) / 2.0
    span = max(max(xs) - min(xs), max(ys) - min(ys), 10.0)
    half = span / 2.0 * MARGIN
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)


def _draw_2d(ax: plt.Axes, system: System) -> None:
    ax.cla()
    for star in system.stars:
        s = 20 * star.radius ** 2
        ax.scatter(
            star.position[0], star.position[1], s=s,
        )
        ax.plot(star.tail[:, 0], star.tail[:, 1])
    ax.scatter(0, 0, c="grey", s=5, zorder=0)
    ax.set_aspect("equal", adjustable="box")
    _auto_zoom_2d(ax, system)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def _draw_3d(ax: plt.Axes, system: System) -> None:
    ax.cla()
    for star in system.stars:
        s = 20 * star.radius ** 2
        ax.scatter(
            star.position[0], star.position[1],
            star.position[2], s=s,
        )
        ax.plot3D(
            star.tail[:, 0], star.tail[:, 1],
            star.tail[:, 2],
        )
    ax.scatter(0, 0, 0, c="grey", s=5, zorder=0)
    ax.set_axis_off()
    # Auto-zoom: fit all stars with margin
    pos = np.array([s.position for s in system.stars])
    center = pos.mean(axis=0)
    span = np.abs(pos - center).max()
    half = max(span, 5.0) * MARGIN
    for i, dim in enumerate("xyz"):
        getattr(ax, f"set_{dim}lim")(
            center[i] - half, center[i] + half,
        )


# ── Entry point ──────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="N-body gravitational simulation",
    )
    parser.add_argument(
        "--3d", dest="three_d", action="store_true",
        help="Render in 3D",
    )
    args = parser.parse_args()

    system = build_default_system()

    if args.three_d:
        ax = plt.subplot(
            projection="3d", proj_type="persp",
        )
        draw = _draw_3d
    else:
        ax = plt.subplot()
        draw = _draw_2d

    def animate(_frame: int) -> None:
        draw(ax, system)
        system.update()

    _ = FuncAnimation(
        plt.gcf(), animate, interval=INTERVAL_MS,
    )
    plt.show()


if __name__ == "__main__":
    main()
