# Three-Body Problem Simulation

Real-time N-body gravitational simulation with auto-zoom camera.

## Setup

```bash
uv sync
```

## Simulation (matplotlib)

```bash
uv run python python_version/main.py          # 2D
uv run python python_version/main.py --3d     # 3D
```

## Screen Saver (pygame)

Fullscreen, exits on any key/click/mouse movement.

```bash
uv sync --group screensaver
uv run python screensaver/fullscreen_saver.py
uv run python screensaver/fullscreen_saver.py --config path/to/custom.toml
```

## Native .saver bundle (macOS System Settings)

```bash
uv sync --group saver-bundle
cd screensaver
uv run python setup.py py2app
cp -r dist/ThreeBodySaver.saver ~/Library/Screen\ Savers/
```

## Configuration

Edit `screensaver/config.toml` to customize:

- `[physics]` — G, dt, steps_per_frame
- `[display]` — fps, tail_length, star_scale, star_min/max_size, background
- `[zoom]` — margin, damping, min/max_scale
- `[[stars]]` — mass, position, velocity, color (6-digit hex)

## How it works

Three stars interact via Newtonian gravity using velocity-Verlet
integration in the center-of-mass rest frame. The camera auto-zooms
with configurable damping to keep all stars in view.
