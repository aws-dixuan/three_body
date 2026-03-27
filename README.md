# Three-Body Screensaver

A real-time gravitational three-body simulation, available as a
macOS screensaver and a matplotlib visualization.

## Install Screensaver (macOS)

```bash
git clone https://github.com/YOUR_USERNAME/three_body.git
cd three_body
./install.sh
```

Requires Xcode command line tools (`xcode-select --install`).

After install, go to System Settings > Screen Saver and select
"ThreeBodySaver". To test immediately:

```bash
open -a ScreenSaverEngine
```

To uninstall:

```bash
./uninstall.sh
```

## Matplotlib Simulation

Interactive matplotlib version with 2D and 3D views.

```bash
uv sync
uv run python python_version/main.py          # 2D
uv run python python_version/main.py --3d     # 3D
```

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

## Standalone Fullscreen (pygame)

Runs fullscreen without installing as a system screensaver.
Exits on any key, click, or mouse movement.

```bash
uv sync --group screensaver
uv run python screensaver/fullscreen_saver.py
```

## Configuration

Edit `screensaver/config.toml` to customize the simulation.
For the installed screensaver, edit the copy at:
`~/Library/Screen Savers/ThreeBodySaver.saver/Contents/Resources/config.toml`

```toml
[physics]
G = 0.667430              # gravitational constant (scaled)
dt = 0.005                # integration timestep
steps_per_frame = 10      # substeps per rendered frame

[display]
fps = 60
tail_length = 2000        # number of trail points
star_scale = 0.25         # star body size multiplier
star_min_size = 7         # min star radius (px)
star_max_size = 30        # max star radius (px)
background = "000510"     # 6-digit hex color

[zoom]
margin = 2.3              # padding around bounding box
damping = 1e-3            # zoom smoothing (lower = slower)
min_scale = 1.0           # most zoomed out
max_scale = 50.0          # most zoomed in

[[stars]]
mass = 100.0
position = [10.0, 10.0]
velocity = [-4.0, -3.4]
color = "0B7E9D"
```

Add or remove `[[stars]]` sections to change the number of bodies.

## Project Structure

```
three_body/
├── python_version/          # matplotlib simulation
│   ├── main.py              # entry point (2D/3D)
│   ├── star.py              # Star class (numpy)
│   └── system.py            # N-body system (numpy)
├── screensaver/
│   ├── config.toml          # shared configuration
│   ├── fullscreen_saver.py  # pygame screensaver
│   └── wrapper/
│       └── main.m           # native macOS .saver (Obj-C)
├── install.sh               # build & install .saver
├── uninstall.sh
└── pyproject.toml
```

## How It Works

Three stars with different masses interact via Newtonian gravity
(`F = G·m₁·m₂/r²`). Integration uses the velocity-Verlet (leapfrog)
method. The system is shifted into the center-of-mass rest frame at
startup so the view stays centered. An auto-zoom camera with
configurable damping keeps all bodies in view.
