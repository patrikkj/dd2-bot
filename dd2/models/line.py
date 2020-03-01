import numpy as np

import dd2.utils as utils

class Line():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.compute()
    
    def compute(self):
        self.vector = utils.math.vector_between_points(self.p1, self.p2)
        self.norm = np.sqrt(np.dot(self.vector, self.vector))
        self.unit_vector = self.vector / self.norm
        self.angle = utils.math.get_angle(*self.vector)

    def find_nearest_point(self, coord):
        distance = np.dot(coord - self.p1, self.vector) / self.norm
        return self.p1 + self.unit_vector * np.clip(distance, 0, self.norm)

    def find_ease_in_out(self, t):
        return self.p1 + self.vector * utils.math.ease_in_out(t, alpha=1)