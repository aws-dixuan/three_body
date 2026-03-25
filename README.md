# Three-Body Problem Simulation

Real-time N-body gravitational simulation using matplotlib.

## Usage

```bash
# 2D projection (default)
python python_version/main.py

# 3D interactive view
python python_version/main.py --3d
```

## Requirements

- Python 3.10+
- numpy
- matplotlib

## How it works

Three stars with different masses interact via Newtonian gravity.
The simulation uses velocity-Verlet (leapfrog) integration and
shifts into the center-of-mass rest frame so the view stays
centered.
