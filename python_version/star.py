import numpy as np



class star:
    def __init__(self, mass, position, velocity, track_length):
        self.mass = mass
        self.radius = np.cbrt(self.mass)
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.track_length = track_length
        self.tail = np.array([self.position])

    def update(self, acceleration, delta_t):
        increment = delta_t * acceleration / 2
        self.velocity += increment
        self.position += self.velocity * delta_t
        self.velocity += increment
        self.tail = np.append(self.tail, [self.position], axis=0)
        if len(self.tail) > self.track_length:
            self.tail = self.tail[-self.track_length:]

    def plot(self):
        return self.position, self.radius, self.tail
