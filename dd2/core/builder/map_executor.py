from functools import singledispatch

import dd2.game as game

from . import events
from .handlers.hero_swap_handler import HeroSwapEventHandler
from .handlers.kinematic_handler import KinematicEventHandler
from .handlers.path_traverse_handler import PathTraverseEventHandler
from .handlers.placement_handler import PlacementEventHandler

# Session
session = game.session.get()

@singledispatch
def consume(event, client):
    raise NotImplementedError(f"Cannot execute event of type {event}")

hero_swap_handler = HeroSwapEventHandler()
@consume.register(events.HeroSwapEvent)
def _(event, client):
    return hero_swap_handler.consume(event, client)

kinematic_handler = KinematicEventHandler()
@consume.register(events.KinematicEvent)
def _(event, client):
    return kinematic_handler.consume(event, client)

path_traverse_handler = PathTraverseEventHandler()
@consume.register(events.PathTraverseEvent)
def _(event, client):
    return path_traverse_handler.consume(event, client)

placement_handler = PlacementEventHandler()
@consume.register(events.PlacementEvent)
def _(event, client):
    return placement_handler.consume(event, client)


def execute(sequence):
    for event in sequence:
        print(f'Consuming event: {event}')
        consume(event, session['client_active'])
