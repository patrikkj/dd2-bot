import dd2.game as game
import dd2.utils.decorators as decorators

from . import event

session = game.session.get()


@decorators.json_serializable
class PathTraverseEvent(event.Event):
    def __init__(self, coords, weights, smooth_factor, n_factor, k):
        self.coords = coords
        self.weights = weights
        self.smooth_factor = smooth_factor
        self.n_factor = n_factor
        self.k = k

    @staticmethod
    def create():
        pass
