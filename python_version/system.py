import numpy as np

# F = G * m1 * m2 / (r^2)
# G = 6.67430e-11  # N*m^2*kg*-2
G = 6.67430e-1  # N*m^2*kg*-2


def dist(star1, star2):
    dist_vector = star1.position - star2.position
    norm = np.linalg.norm(dist_vector)
    unit_dist = np.array(dist_vector / norm)
    return unit_dist, norm


class system:
    def __init__(self, stars, delta_t):
        self.stars = stars  # a list of class star
        self.delta_t = delta_t
        # set mass center position and speed to zero
        total_momentum = np.zeros(stars[0].position.shape)
        total_mass = 0
        mass_center = np.zeros(stars[0].position.shape)
        for star in stars:
            total_momentum += star.mass * star.velocity
            total_mass += star.mass
            mass_center += star.mass * star.position
        print(total_momentum)
        for star in stars:
            star.velocity -= total_momentum / total_mass
            star.position -= mass_center / total_mass
            star.tail = np.array([star.position])


    def update(self):
        resultant_accelerations = []
        for star in self.stars:
            resultant_acceleration = np.zeros(star.position.shape)
            for other in self.stars:
                if other != star:
                    unit_dist, norm = dist(star, other)
                    acceleration = np.array(unit_dist * G * other.mass / norm)
                    resultant_acceleration -= acceleration
            resultant_accelerations.append(resultant_acceleration)
        for i in range(len(self.stars)):
            self.stars[i].update(np.array(resultant_accelerations[i]), self.delta_t)

    def show_stars(self):
        for star in self.stars:
            print(star.plot())
