import time
import warnings

import cv2.cv2 as cv2
import numpy as np

import dd2.core.builder as builder
import dd2.core.kinematics as kinematics
import dd2.game as game
import dd2.io as io
import dd2.utils.enums as enums


def initialize():
    session = game.session.get()

    _initialize_session(session)
    _initialize_hotkeys(session)
    _initialize_event_hooks(session)
    _initialize_main_client(session)

    warnings.simplefilter("ignore", category=UserWarning)
    io.win.set_console_position(0, 210, 320, 720)
    return session

def _initialize_hotkeys(session):
    hotkey_to_callback = {
        "numpad_1": lambda *_: builder.builder.start_defense_placement(session['client_active'].get_defense(enums.Slot.DEFENSE_1)),
        "numpad_2": lambda *_: builder.builder.start_defense_placement(session['client_active'].get_defense(enums.Slot.DEFENSE_2)),
        "numpad_3": lambda *_: builder.builder.start_defense_placement(session['client_active'].get_defense(enums.Slot.DEFENSE_3)),
        "numpad_4": lambda *_: builder.builder.start_defense_placement(session['client_active'].get_defense(enums.Slot.DEFENSE_4)),
        "numpad_5": lambda *_: builder.builder.extend_node_chain(),
        "numpad_6": lambda *_: builder.builder.append_event(builder.events.HeroSwapEvent.create()),
        "numpad_7": lambda *_: builder.builder.append_event(builder.events.MoveEvent.create()),
        "numpad_8": lambda *_: builder.builder.append_event(builder.events.JumpEvent.create()),
        "numpad_9": lambda *_: builder.builder.append_event(builder.events.MoveRotateEvent.create()),
        "numpad_0": lambda *_: builder.builder.end_defense_placement(),
        "numpad_plus": lambda *_: builder.builder.start_recording(),
        "numpad_minus": lambda *_: builder.builder.end_recording(),
        "numpad_divide": lambda *_: builder.builder.load_all_maps(),
        "numpad_multiply": lambda *_: builder.builder.print_loaded_maps(),
        "numpad_decimal": lambda *_: builder.builder.build_sequence_select(),

        "shift+numpad_1": lambda *_: print(session['client_active'].player_coords.read(), time.perf_counter()),
        "shift+numpad_2": lambda *_: session['client_active'].rotation.read(),
        "shift+numpad_3": lambda *_: session['client_active'].map_data.read(),
        "shift+numpad_4": lambda *_: session['client_active'].player_du.read(),
        "shift+numpad_5": lambda *_: utils.get_wave_count(session['client_active'].hwnd),
        "shift+numpad_6": lambda *_: utils.get_mob_count(session['client_active'].hwnd),
        "shift+numpad_7": lambda *_: utils.get_hero_slot(session['client_active'].hwnd),
        "shift+numpad_8": lambda *_: builder.builder.dump_sequence(),
        "shift+numpad_9": lambda *_: session.display(),
        "shift+numpad_0": lambda *_: game.state.select_state(session),

        "ctrl+pgup": lambda *_: None,
        "ctrl+pgdn": lambda *_: None,
        "ctrl+numpad_plus": lambda *_: builder.builder.start_path(),
        "ctrl+numpad_minus": lambda *_: builder.builder.end_path(),
        "ctrl+numpad_1": lambda *_: builder.builder.extend_path(1),
        "ctrl+numpad_2": lambda *_: builder.builder.extend_path(2),
        "ctrl+numpad_3": lambda *_: builder.builder.extend_path(3),
        "ctrl+numpad_4": lambda *_: kinematics.rotate_yaw(session['client_active'], -0.5), # Left
        "ctrl+numpad_5": lambda *_: kinematics.rotate_yaw(session['client_active'], -1), # Down
        "ctrl+numpad_6": lambda *_: kinematics.rotate_yaw(session['client_active'], 0.5), # Right
        "ctrl+numpad_7": lambda *_: kinematics.rotate_pitch(session['client_active'], -0.5),
        "ctrl+numpad_8": lambda *_: kinematics.rotate_yaw(session['client_active'], 0), # Up
        "ctrl+numpad_9": lambda *_: kinematics.rotate_pitch(session['client_active'], 0.5),
        # "ctrl+numpad_0": lambda *_: kinematics.set_yaw(session['client_active'], -0.5),

        # "altgr+pgup": lambda *_: kinematics.increase_gain(0.1),
        # "altgr+pgdn": lambda *_: kinematics.decrease_gain(0.1),
        "altgr+numpad_plus": lambda *_: builder.builder.start_path(),
        "altgr+numpad_minus": lambda *_: builder.builder.end_path(),
        "altgr+numpad_1": lambda *_: kinematics.move(session['client_active'], np.array((300, 300)), relative=True),
        "altgr+numpad_2": lambda *_: kinematics.move(session['client_active'], np.array((-300, 300)), relative=True),
        "altgr+numpad_3": lambda *_: kinematics.move(session['client_active'], np.array((300, -300)), relative=True),
        "altgr+numpad_4": lambda *_: kinematics.rotate(session['client_active'], np.array((0, -0.5))), # Left
        "altgr+numpad_5": lambda *_: kinematics.rotate(session['client_active'], np.array((0, -1))), # Down
        "altgr+numpad_6": lambda *_: kinematics.rotate(session['client_active'], np.array((0, 0.5))), # Right
        "altgr+numpad_7": lambda *_: kinematics.rotate(session['client_active'], np.array((0.5, -0.5))),
        "altgr+numpad_8": lambda *_: kinematics.rotate(session['client_active'], np.array((0, 0))), # Up
        "altgr+numpad_9": lambda *_: kinematics.rotate(session['client_active'], np.array((0.5, 0.5))),
        # "altgr+numpad_0": lambda *_: kinematics.set_yaw(session['client_active'], -0.5),

        # "w": lambda *_: io.keyboard.set_input_y(session['client_main'], 1),
        # "a": lambda *_: io.keyboard.set_input_x(session['client_main'], -1),
        # "s": lambda *_: io.keyboard.set_input_y(session['client_main'], -1),
        # "d": lambda *_: io.keyboard.set_input_x(session['client_main'], 1),

        "f1": lambda *_: session['client_active'].set_active_hero_slot(enums.Slot.HERO_1),
        "f2": lambda *_: session['client_active'].set_active_hero_slot(enums.Slot.HERO_2),
        "f3": lambda *_: session['client_active'].set_active_hero_slot(enums.Slot.HERO_3),
        "f4": lambda *_: session['client_active'].set_active_hero_slot(enums.Slot.HERO_4),
        "f5": lambda *_: io.win.set_focus_console(),
        "f7": lambda *_: builder.builder.print_coords_from_selected(),
        "f8": lambda *_: io.file.save_image(io.screen.capture_window(session['client_active'])),
        "pause": lambda *_: session.set('pause', not session['pause']),
        "ctrl+esc": lambda *_: io._keyboard.this.EXIT,
    }
    io.keyboard.add_hotkeys(hotkey_to_callback)

def _initialize_session(session):
    # Fetch HWND's
    # clients = sorted(io.win.get_windows(identifier="Dungeon Defenders 2 [#]"), key=lambda tup: tup[1])
    windows = sorted(io.win.get_windows(identifier="Dungeon Defenders 2"), key=lambda tup: tup[1])
    hwnds = [window[0] for window in windows]
    clients = [game.client.Client(hwnd) for hwnd in hwnds]
    session['clients'] = clients
    session['client_hwnds'] = hwnds
    session['client_count'] = len(clients)
    session['client_active'] = clients[0]
    session['client_main'] = clients[0]
    session['state'] = game.state.Idle
    session['wave'] = None
    session['pause'] = False
    session['auto_build'] = True
    session['auto_build_map_prefix'] = "MAP_Drakenfrost_Resort"
    # session.display()

def _initialize_event_hooks(session):
    def _on_win_event(_, hwnd, title):
        if hwnd in session['client_hwnds']:
            print(f"Active client: {(hwnd, title[:8])}")
            session['client_active'] = next(c for c in session['clients'] if c.hwnd == hwnd)
    io.win.add_win_event_hook(_on_win_event)

def _initialize_main_client(session):
    client_main = session['client_main'] 

    # Create movement injection service for writing input to process
    io.keyboard.create_service(client_main)

    # Set active hero configuration
    client_main.set_hero_slot_mapping({
        enums.Slot.HERO_1: {
            enums.Defense.EARTHSHATTER_TOWER
        },
        enums.Slot.HERO_2: {
            enums.Defense.PROTON_BEAM,
            enums.Defense.REFLECT_BEAM
        },
        enums.Slot.HERO_3: {
            enums.Defense.FLAME_AURA,
            enums.Defense.BOOST_AURA,
            enums.Defense.SKY_GUARD_TOWER,
            enums.Defense.LIGHTNING_STRIKE_AURA
        },
        enums.Slot.HERO_4: {
            enums.Defense.BONE_ARCHERS
        }
    })


def run(session):
    # status_code = -0x1
    print(f"Executing from state: {session['state']}")
    
    # Detect initial state
    state_map = {
        enums.State.PRE_INIT_BUILD_PHASE: game.state.PreInitBuildPhase,
        enums.State.INIT_BUILD_PHASE: game.state.InitBuildPhase,
        enums.State.COMBAT_PHASE: game.state.CombatPhase,
        enums.State.PRE_BUILD_PHASE: game.state.PreBuildPhase,
        enums.State.BUILD_PHASE: game.state.BuildPhase,
        enums.State.POST_COMBAT_PHASE: game.state.PostCombatPhase,
        enums.State.SUMMARY_SCREEN: game.state.SummaryScreen,
        enums.State.TOWN: game.state.Town,
        enums.State.PRIVATE_TAVERN: game.state.Tavern
    }
    
    # Loop until valid state
    _state = session['client_main'].state.read()
    while not _state:
        _state = session['client_main'].state.read()
    
    print(f"State detected: {_state}")
    session['state'] = state_map[_state]
    session['state'] = game.state.Idle
# session['state'] 
    while io._keyboard.this.status_code != io._keyboard.this.EXIT:
        cached_state = session['state']
        session['state'] = session['state'].execute(session)
        if session['state'] != cached_state:
            print(f"State change from {cached_state} to {session['state']}.")

        while session['pause']:
            cv2.waitKey(20) & 0xFF
        cv2.waitKey(2) & 0xFF


def main():
    session = initialize()
    run(session)
