"""N-body gravitational system with center-of-mass frame correction."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from star import Star

# Scaled gravitational constant (not physical — tuned for visuals)
G: float = 6.67430e-1


class System:
    """A collection of Stars interacting via Newtonian gravity.

    On construction the system shifts all bodies into the
    center-of-mass rest frame so the view stays centered.

    Attributes:
        stars: The bodies in the simulation.
        dt: Integration timestep.
    """

    def __init__(self, stars: list[Star], dt: float = 0.1) -> None:
        self.stars = stars
        self.dt = dt
        self._center_frame()

    def update(self) -> None:
        """Compute accelerations, advance every body one timestep."""
        accelerations = self._compute_accelerations()
        for star, acc in zip(self.stars, accelerations):
            star.update(acc, self.dt)

    def _center_frame(self) -> None:
        """Shift to center-of-mass rest frame."""
        total_mass = sum(s.mass for s in self.stars)
        total_p = sum(s.mass * s.velocity for s in self.stars)
        com = (
            sum(s.mass * s.position for s in self.stars)
            / total_mass
        )
        for star in self.stars:
            star.velocity -= total_p / total_mass
            star.position -= com
            star.tail = np.array([star.position.copy()])

    def _compute_accelerations(
        self,
    ) -> list[NDArray[np.float64]]:
        """Return net gravitational acceleration per body."""
        accelerations: list[NDArray[np.float64]] = []
        for star in self.stars:
            acc = np.zeros_like(star.position)
            for other in self.stars:
                if other is star:
                    continue
                d, r = _direction_and_distance(star, other)
                acc -= d * G * other.mass / r
            accelerations.append(acc)
        return accelerations


def _direction_and_distance(
    a: Star, b: Star,
) -> tuple[NDArray[np.float64], float]:
    """Unit vector from b toward a, and scalar distance."""
    delta = a.position - b.position
    dist = float(np.linalg.norm(delta))
    return delta / dist, dist
