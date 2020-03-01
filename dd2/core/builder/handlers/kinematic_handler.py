from functools import singledispatchmethod

import dd2.core.kinematics as kinematics

from ..events import kinematic_event
from . import event_handler


class KinematicEventHandler(event_handler.EventHandler):
    @singledispatchmethod
    def consume(self, event, client):
        raise NotImplementedError(f"Cannot consume event of type {event}")

    @consume.register(kinematic_event.MoveEvent)
    def _(self, event, client):
        return kinematics.move(client, event.coords, relative=event.relative)

    @consume.register(kinematic_event.RotateEvent)
    def _(self, event, client):
        return kinematics.rotate(client, event.rotation)

    @consume.register(kinematic_event.MoveRotateEvent)
    def _(self, event, client):
        return kinematics.move_rotate(client, event.coords, event.rotation, event.relative)

    @consume.register(kinematic_event.JumpEvent)
    def _(self, event, client):
        return kinematics.jump(client, event.coords, event.relative)
