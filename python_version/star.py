"""Celestial body for N-body gravitational simulation."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class Star:
    """A massive body in the simulation.

    Tracks position, velocity, mass, and a tail of recent
    positions for trajectory visualization.
    """

    def __init__(
        self,
        mass: float,
        position: list[float],
        velocity: list[float],
        tail_length: int = 200,
    ) -> None:
        self.mass = mass
        self.radius = float(np.cbrt(mass))
        self.position: NDArray[np.float64] = np.array(
            position, dtype=np.float64,
        )
        self.velocity: NDArray[np.float64] = np.array(
            velocity, dtype=np.float64,
        )
        self.tail_length = tail_length
        self.tail: NDArray[np.float64] = np.array(
            [self.position.copy()],
        )

    def update(
        self,
        acceleration: NDArray[np.float64],
        dt: float,
    ) -> None:
        """Advance one timestep (velocity-Verlet / leapfrog).

        Args:
            acceleration: Net acceleration vector.
            dt: Timestep duration.
        """
        half_kick = 0.5 * dt * acceleration
        self.velocity += half_kick
        self.position += self.velocity * dt
        self.velocity += half_kick

        self.tail = np.append(
            self.tail, [self.position.copy()], axis=0,
        )
        if len(self.tail) > self.tail_length:
            self.tail = self.tail[-self.tail_length:]
