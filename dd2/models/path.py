import numpy as np
from scipy import interpolate

import dd2.utils as utils


class Path():
    def __init__(self, coords, weights=None, smooth_factor=1000, n_factor=100, k=3):
        if weights is None:
            self.m = len(coords)
            weights = np.ones(self.m)

        self.update_params(coords=coords, weights=weights, smooth_factor=smooth_factor, n_factor=n_factor, k=k)
        self.interpolate_()
        self.discretize()

    def update_params(self, coords=None, weights=None, smooth_factor=None, n_factor=None, k=None):
        if coords is not None:
            self.coords = coords
            self.m = len(coords)
            self.x, self.y, *_ = coords.transpose()
        if weights is not None:
            self.weights = weights
        if smooth_factor is not None:
            self.smooth_factor = smooth_factor
            self.s = smooth_factor * (self.m+(2*self.m)**0.5)
        if n_factor is not None:
            self.n_factor = n_factor
            self.n = (self.m - 1) * self.n_factor
        if k is not None:
            self.k = k

    def interpolate_(self):
        self.tck, self.u = interpolate.splprep([self.x, self.y], self.weights, s=self.s, k=self.k)
        
    def discretize(self):
        self.t = np.linspace(0, 1, self.n)
        self.solutions = self.evaluate(self.t, der=0)
        self.derivatives = self.evaluate(self.t, der=1)
        self.derivatives_2 = self.evaluate(self.t, der=2)
        self.distances = np.insert(utils.math.euclidean_distance(self.solutions[:,1:], self.solutions[:,:-1], row_per_axis=True), 0, 0)
        self.distances_cumulative = self.distances.cumsum()

    def evaluate(self, t, der=0):
        return np.array(interpolate.splev(t, self.tck, der=der))

    def evaluate_angle(self, t):
        dx, dy = self.evaluate(t, der=1)
        return utils.math.get_angle(dx, dy)

    # @timeit
    def find_nearest_point(self, coord):
        ''' Returns: (x, y), distance, theta, t '''
        distances = utils.math.euclidean_distance(self.solutions, coord, row_per_axis=True)
        i = np.argmin(distances) 
        theta = utils.math.get_angle(*self.derivatives[:,i])
        return self.solutions[:,i], distances[i], theta, self.t[i]
        
    # @timeit
    def find_nearest_point_iterative(self, coord, t_prev, MAX_ITER_DISTANCE=200):
        ''' Returns: (x, y), distance, theta, t '''
        i_prev = self.t.searchsorted(t_prev)
        distance_cap = self.distances_cumulative[i_prev] + MAX_ITER_DISTANCE
        i_cap = self.distances_cumulative.searchsorted(distance_cap)
        
        # Find closest point
        candidates = utils.math.euclidean_distance(self.solutions[:,i_prev:i_cap], coord, row_per_axis=True)
        i_nearest = np.argmin(candidates) 
        # print(candidates)
        theta = utils.math.get_angle(*self.derivatives[:,i_prev + i_nearest])
        return self.solutions[:,i_prev + i_nearest], candidates[i_nearest], theta, self.t[i_prev + i_nearest]

    def _distance_to_point(self, t, coord):
        x, y = self.evaluate(t)
        return (coord[0] - x) ** 2 + (coord[1] - y) ** 2
