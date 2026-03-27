# Three-Body Problem Simulation

Real-time N-body gravitational simulation with auto-zoom camera.

## Install Screensaver (macOS)

```bash
git clone https://github.com/YOUR_USERNAME/three_body.git
cd three_body
./install.sh
```

Requires Python 3.10+, [uv](https://docs.astral.sh/uv/getting-started/installation/), and Xcode command line tools (`xcode-select --install`).

After install:
1. Open System Settings > Screen Saver
2. Select "ThreeBodySaver"
3. Test immediately: `open -a ScreenSaverEngine`

To customize colors, speed, zoom: edit
`~/Library/Screen Savers/ThreeBodySaver.saver/Contents/Resources/config.toml`

To uninstall: `./uninstall.sh`

## Simulation (matplotlib)

```bash
uv sync
uv run python python_version/main.py          # 2D
uv run python python_version/main.py --3d     # 3D
```

## Standalone Screensaver (no install)

```bash
uv sync --group screensaver
uv run python screensaver/fullscreen_saver.py
```

## Configuration

Edit `screensaver/config.toml` to customize:

- `[physics]` — G, dt, steps_per_frame
- `[display]` — fps, tail_length, star_scale, star_min/max_size, background (hex)
- `[zoom]` — margin, damping, min/max_scale
- `[[stars]]` — mass, position, velocity, color (6-digit hex)

## How it works

Three stars interact via Newtonian gravity using velocity-Verlet
integration in the center-of-mass rest frame. The camera auto-zooms
with configurable damping to keep all stars in view.
