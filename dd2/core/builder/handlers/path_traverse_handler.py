import dd2.core.kinematics as kinematics
import dd2.models as models

from . import event_handler


class PathTraverseEventHandler(event_handler.EventHandler):
    def consume(self, event, client):
        return kinematics.traverse_path(client, 
            models.path.Path(event.coords, event.weights, event.smooth_factor, event.n_factor, event.k))
