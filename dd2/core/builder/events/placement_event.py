import dd2.game as game
import dd2.utils.decorators as decorators

from . import event

session = game.session.get()

        
@decorators.json_serializable
class PlacementEvent(event.Event):
    def undo(self):
        pass

    @staticmethod
    def create(defense):
        pass

        
@decorators.json_serializable
class TowerPlacementEvent(PlacementEvent):
    def __init__(self, start_orientation, end_orientation, defense):
        self.start_orientation = start_orientation
        self.end_orientation = end_orientation
        self.defense = defense


@decorators.json_serializable
class NodePlacementEvent(PlacementEvent):
    def __init__(self, orientations_2d, defense):
        self.orientations_2d = orientations_2d
        self.defense = defense


@decorators.json_serializable
class AuraPlacementEvent(PlacementEvent):
    def __init__(self, orientation_2d, defense):
        self.orientation_2d = orientation_2d
        self.defense = defense
