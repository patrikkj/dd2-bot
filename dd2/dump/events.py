import sys
import time
import cv2.cv2 as cv2
import numpy as np
from abc import ABC, abstractmethod
from dd2 import session as sess
from dd2.utils import utils, templates
from dd2.kinematics import kinematics
from dd2.kinematics.path import Path
import dd2.io as io
from dd2.io.file_io import json_serializable
from collections import namedtuple

# Session
session = sess.get()

@common.decorators.json_serializable
class Event(ABC):
    @abstractmethod
    def fire(self):
        pass

    def __str__(self):
        return self.__class__.__name__


@json_serializable
class MoveEvent(Event):
    def __init__(self, coords, relative):
        self.coords = coords
        self.relative = relative

    @staticmethod
    def create(relative=False):
        return MoveEvent(
            session['client_active'].player_coords_2d.read(), 
            relative=relative
        )

    def fire(self):
        return kinematics.move(session['client_active'],
                               self.coords,
                               relative=self.relative)

@json_serializable
class JumpEvent(Event):
    def __init__(self, coords, relative):
        self.coords = coords
        self.relative = relative

    @staticmethod
    def create(relative=False):
        return JumpEvent(
            session['client_active'].player_coords_2d.read(), 
            relative=relative
        )

    def fire(self):
        return kinematics.jump(session['client_active'],
                               self.coords,
                               relative=self.relative)


@json_serializable
class RotateEvent(Event):
    def __init__(self, rotation):
        self.rotation = rotation

    @staticmethod
    def create():
        return RotateEvent(session['client_active'].rotation.read())

    def fire(self):
        return kinematics.rotate(session['client_active'], self.rotation)


@json_serializable
class MoveRotateEvent(Event):
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

    def fire(self):
        return kinematics.move_rotate(
            session['client_active'],
            self.coords,
            self.rotation,
            relative=self.relative
        )


@json_serializable
class PathTraverseEvent(Event):
    def __init__(self, coords, weights, smooth_factor, n_factor, k):
        self.coords = coords
        self.weights = weights
        self.smooth_factor = smooth_factor
        self.n_factor = n_factor
        self.k = k

    @staticmethod
    def create():
        pass

    def fire(self):
        return kinematics.traverse_path(
            session['client_active'],
            Path(self.coords, self.weights, self.smooth_factor, self.n_factor, self.k)
        )


@json_serializable
class HeroSwapEvent(Event):
    def __init__(self, hero_slot):
        self.hero_slot = hero_slot

    @staticmethod
    def create():
        return HeroSwapEvent(utils.get_hero_slot(session['client_active'].hwnd))

    def fire(self):
        while utils.get_hero_slot(session['client_active'].hwnd) != self.hero_slot:
            io.keyboard.press_and_release(self.hero_slot.value)
            time.sleep(0.2)
        return utils.get_hero_slot(session['client_active'].hwnd)

        
@json_serializable
class TowerPlacementEvent(Event):
    is_building = False
    cached_orientation = None

    def __init__(self, start_orientation, end_orientation, defense):
        self.start_orientation = start_orientation
        self.end_orientation = end_orientation
        self.defense = defense

    @classmethod
    def create(cls, defense):
        pass

    def fire(self):
        client = session['client_main']
        start_coords, start_rotation = self.start_orientation
        end_coords, end_rotation = self.end_orientation

        # Change character if nessecary
        required_hero_slot = client.get_hero_slot(self.defense)
        if client.get_active_hero_slot() != required_hero_slot:
            utils.set_hero_slot(client, required_hero_slot)

        # Place defense
        du_current = client.du_current.read()
        du_target = du_current + self.defense.initial_cost

        def _inner_loop():
            utils.do_until(
                callable_=lambda *_: io.keyboard.press_and_release(self.defense.defense_slot.get_hotkey()),
                test=client.interactive_mode.read,
            )

            kinematics.move_rotate(client, start_coords, start_rotation, relative=False)
            time.sleep(0.4)
            io.mouse.click()
            kinematics.move_rotate(client, end_coords, end_rotation, relative=False)
            time.sleep(0.4)
            io.mouse.click()

        utils.do_until(
                callable_=_inner_loop,
                test=client.du_current.read,
                target_value=du_target,
                on_retry=lambda *_: (io.mouse.right_click(), time.sleep(0.2)),
                retry=5,
                timeout=20
            )

@json_serializable
class NodePlacementEvent(Event):
    def __init__(self, orientations_2d, defense):
        self.orientations_2d = orientations_2d
        self.defense = defense

    @staticmethod
    def create(defense):
        pass

    def fire(self):
        client = session['client_main']

        # Change character if nessecary
        required_hero_slot = client.get_hero_slot(self.defense)
        if client.get_active_hero_slot() != required_hero_slot:
            utils.set_hero_slot(client, required_hero_slot)

        # Place defense
        du_current = client.du_current.read()
        initial_cost = self.defense.initial_cost 
        chain_cost = self.defense.extension_cost * (len(self.orientations_2d) - 2)
        du_target = du_current + initial_cost + chain_cost

        def _inner_loop():
            node_counter = client.node_counter.read()

            utils.do_until(
                callable_=lambda *_: io.keyboard.press_and_release(self.defense.defense_slot.get_hotkey()),
                test=client.interactive_mode.read
            )

            for i, orientation_2d in enumerate(self.orientations_2d):
                coords, rotation = orientation_2d
                node_counter_target = (node_counter + i) % 7 + 1
                utils.do_until(
                    callable_=lambda *_: (
                        kinematics.move_rotate(client, coords, rotation, relative=False),
                        time.sleep(0.4),
                        io.mouse.click(),
                    ),
                    test=client.node_counter.read,
                    target_value=node_counter_target,
                    on_retry=lambda *_: (
                        io.win.set_focus(client.hwnd),
                        io.win.set_mouse_capture(client.hwnd)
                    )
                )
            utils.do_until(
                callable_=lambda *_: io.keyboard.press_and_release("e"),
                test=client.interactive_mode.read,
                target_value=False
            )
            
        utils.do_until(
                callable_=_inner_loop,
                test=client.du_current.read,
                target_value=du_target,
                retry=5,
                timeout=20
            )


@json_serializable
class AuraPlacementEvent(Event):
    def __init__(self, orientation_2d, defense):
        self.orientation_2d = orientation_2d
        self.defense = defense

    @staticmethod
    def create(defense):
        pass

    def fire(self):
        client = session['client_main']
        coords, rotation = self.orientation_2d

        # Change character if nessecary
        required_hero_slot = client.get_hero_slot(self.defense)
        if client.get_active_hero_slot() != required_hero_slot:
            utils.set_hero_slot(client, required_hero_slot)

        # Place defense
        du_current = client.du_current.read()
        du_target = du_current + self.defense.initial_cost

        def _inner_loop():
            utils.do_until(
                callable_=lambda *_: io.keyboard.press_and_release(self.defense.defense_slot.get_hotkey()),
                test=client.interactive_mode.read
            )

            utils.do_until(
                callable_=lambda *_: (
                    kinematics.move_rotate(client, coords, rotation, relative=False),
                    time.sleep(0.4),
                    io.mouse.click()
                ),
                test=client.interactive_mode.read,
                target_value=False
            )
            
        utils.do_until(
            callable_=_inner_loop,
            test=client.du_current.read,
            target_value=du_target,
            retry=5,
            timeout=20
        )
