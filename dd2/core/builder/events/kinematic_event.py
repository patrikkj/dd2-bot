import dd2.game as game
import dd2.utils.decorators as decorators

from . import event

session = game.session.get()


@decorators.json_serializable
class KinematicEvent(event.Event):
    def undo(self):
        pass

    def to_relative(self):
        pass
    

@decorators.json_serializable
class MoveEvent(KinematicEvent):
    def __init__(self, coords, relative):
        self.coords = coords
        self.relative = relative

    @staticmethod
    def create(relative=False):
        return MoveEvent(
            session['client_active'].player_coords_2d.read(), 
            relative=relative
        )


@decorators.json_serializable
class JumpEvent(KinematicEvent):
    def __init__(self, coords, relative):
        self.coords = coords
        self.relative = relative

    @staticmethod
    def create(relative=False):
        return JumpEvent(
            session['client_active'].player_coords_2d.read(), 
            relative=relative
        )


@decorators.json_serializable
class RotateEvent(KinematicEvent):
    def __init__(self, rotation):
        self.rotation = rotation

    @staticmethod
    def create():
        return RotateEvent(session['client_active'].rotation.read())


@decorators.json_serializable
class MoveRotateEvent(KinematicEvent):
    def __init__(self, coords, rotation, relative):
        self.coords = coords
        self.rotation = rotation
        self.relative = relative

    @staticmethod
    def create(relative=False):
        return MoveRotateEvent(
            session['client_active'].player_coords_2d.read(),
            session['client_active'].rotation.read(),
            relative=relative
        )
