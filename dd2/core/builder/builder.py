import os
import sys
from enum import Enum, auto

import numpy as np

import dd2.game as game
import dd2.io as io
import dd2.utils.enums as enums
from dd2.utils import utils

from . import events

# Module level scope pointer
this = sys.modules[__name__]
this.is_recording = False
this.recorded_sequence = []

# Cached event placement
this.cache_active = False
this.cached_defense = None
this.cached_orientations_2d = []

class Status(Enum):
    IDLE = auto()
    RECORDING = auto()
    PATHING = auto()
    CACHING = auto()
this.status = Status.IDLE

# Paths
this.path_active = False
this.path_coords = []
this.path_weights = []

# Loaded maps
this.loaded_maps = {}

# Session
session = game.session.get()

def init():
    load_all_maps()

def start_recording():
    if this.status != Status.IDLE:
        print(f"Start recording failed [status={this.status}]")
        return

    client = session['client_active']
    this.status = Status.RECORDING
    this.recorded_sequence = []
    
    # Updating active hero slot data
    utils.update_hero_slot(client)
    print("Recording started")

def append_event(event, force=False):
    if not force and this.status != Status.RECORDING:
        print(f"Append {event} failed [status={this.status}]")
        return

    print(f"Appending {event}")
    this.recorded_sequence.append(event)

def undo():
    if this.status == Status.IDLE:
        print(f"Undo failed [status={this.status}]")

    elif this.status == Status.RECORDING:
        if this.recorded_sequence:
            print(f"Removed {this.recorded_sequence.pop()} successfully")
        else:
            print(f"Undo failed, empty list [status={this.status}]")

    elif this.status == Status.PATHING:
        if this.path_coords:
            print(f"Removed {this.path_coords.pop()} and {this.path_weights.pop()} successfully")
        else:
            print(f"Undo failed, empty list [status={this.status}]")

    elif this.status == Status.CACHING:
        if this.cached_orientations_2d:
            print(f"Removed {this.cached_orientations_2d.pop()} successfully")
        else:
            print(f"Undo failed, empty list [status={this.status}]")


def start_path():
    if this.status != Status.RECORDING:
        print(f"Start path failed [status={this.status}]")
        return

    print(f"Starting path generation")
    this.status = Status.PATHING
    this.path_coords = [session['client_active'].player_coords_2d.read()]
    this.path_weights = [1]
    
def extend_path(weight):
    if this.status != Status.PATHING:
        print(f"Path extension failed [status={this.status}]")
        return

    print(f"Extending path")
    this.path_coords.append(session['client_active'].player_coords_2d.read())
    this.path_weights.append(weight)

def end_path():
    if this.status != Status.PATHING:
        print(f"Path extension failed [status={this.status}]")
        return
    
    print(f"Terminating path")
    this.path_coords.append(session['client_active'].player_coords_2d.read())
    this.path_weights.append(1)
    this.status = Status.RECORDING
    _coords = np.array(this.path_coords)
    _weights = np.array(this.path_weights)
    
    append_event(events.PathTraverseEvent(_coords, _weights, smooth_factor=1, n_factor=100, k=3), force=True)

def start_defense_placement(defense):
    if this.status != Status.RECORDING:
        print(f"Start def. placement failed [status={this.status}]")
        return

    if defense.defense_type == enums.DefenseType.AURA:
        append_event(events.AuraPlacementEvent(session['client_active'].orientation_2d.read(), defense))
        return

    print(f"Starting placement: {defense}")
    this.status = Status.CACHING
    this.cached_defense = defense
    this.cached_orientations_2d = [session['client_active'].orientation_2d.read()]

def extend_node_chain():
    if this.status != Status.CACHING:
        print(f"Node chain extension failed [status={this.status}]")
        return

    if (def_type := this.cached_defense.defense_type) != enums.DefenseType.NODE:
        print(f"Cannot extend defense of type: {def_type}")
        return

    print(f"Extending node chain: {this.cached_defense}")
    this.cached_orientations_2d.append(session['client_active'].orientation_2d.read())

def end_defense_placement():
    if this.status != Status.CACHING:
        print(f"End def. placement failed [status={this.status}]")
        return
    
    print(f"Terminating placement: {this.cached_defense}")
    this.cached_orientations_2d.append(session['client_active'].orientation_2d.read())
    this.status = Status.RECORDING

    if this.cached_defense.defense_type == enums.DefenseType.TOWER:
        append_event(events.TowerPlacementEvent(*this.cached_orientations_2d, this.cached_defense), force=True)
    elif this.cached_defense.defense_type == enums.DefenseType.NODE:
        append_event(events.NodePlacementEvent(this.cached_orientations_2d, this.cached_defense), force=True)

def end_recording():
    if this.status != Status.RECORDING:
        print(f"End recording failed [status={this.status}]")
        return

    this.status = Status.IDLE
    print("Recording terminated")
    dump_sequence()

def build_sequence(sequence):
    if this.status == Status.RECORDING:
        print(f"Extended recording")
        for event in sequence:
            print(f" + {event}")
        print()
        this.recorded_sequence.extend(sequence)

    for event in sequence:
        print(f"Firing event: {event}")
        event.fire()

def build_sequence_by_name(prefix, exact=False):
    if exact:
        filename, sequence = next((fn, seq) for fn, seq in this.loaded_maps.items() if fn == prefix)
    else:
        filename, sequence = next((fn, seq) for fn, seq in this.loaded_maps.items() if fn.startswith(prefix))
    print(f"Building map: {filename}")
    for event in sequence:
        print(f"Firing event: {event}")
        event.fire()

def build_sequence_select():
    selected = io.keyboard.select_from_options_input(this.loaded_maps)
    build_sequence(selected)

# IO
def print_sequence():
    for event in this.recorded_sequence:
        print(event)

def dump_sequence(indent=4):
    filename = f"{io.keyboard.input_('Build sequence name: ')}.json"
    return io.file.dump_json(this.recorded_sequence, enums.Folder.MAPS_DIR.value, filename=filename, indent=indent)

def load_sequence(prefix, exact=False):
    return io.file.load_json(prefix, enums.Folder.MAPS_DIR.value, exact=exact)

def load_all_maps():
    this.loaded_maps = {fn: load_sequence(fn, exact=True) for fn in os.listdir(enums.Folder.MAPS_DIR.value)}

def print_coords_from_selected():
    x_coords = []
    y_coords = []
    selected = io.keyboard.select_from_options(this.loaded_maps)
    for event in selected:
        if isinstance(event, events.MoveRotateEvent):
            x_coords.append(event.coords[0])
            y_coords.append(event.coords[1])
    print(f"x = np.array({x_coords}")
    print(f"y = np.array({y_coords}")

def print_loaded_maps():
    print(this.loaded_maps)

def rewrite_map_select(indent=4):
    options = {fn: fn for fn in os.listdir(enums.Folder.MAPS_DIR.value)}
    selected = io.keyboard.select_from_options(options)
    return rewrite_map(selected, exact=True, indent=indent)

def rewrite_map(prefix, exact=False, indent=4):
    return io.file.rewrite_json(prefix, enums.Folder.MAPS_DIR.value, exact=exact, indent=indent)

init()
