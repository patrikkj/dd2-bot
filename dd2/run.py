import sys
import time
import warnings
import pywinauto.keyboard as pykeyboard
from enum import Enum, auto


# ------------
from mouse import _winmouse as _os_mouse
# ------------



import cv2.cv2 as cv2

from dd2.client import Client
from dd2.io import file_io, keyboard_io, mouse_io, screen_io, win_io
from dd2.io.helpers import (_file_io, _keyboard_io, _mouse_io, _screen_io,
                            _win_io)

from . import session as sess
from .state import (BuildPhase, CombatPhase, Idle, LoadingScreen,
                    PostCombatPhase, PreBuildPhase, SummaryScreen)
from .utils import image_search, text_search, utils, kinematics


def initialize():
    session = sess.get()

    _initialize_session(session)
    _initialize_hotkeys(session)
    _initialize_event_hooks(session)

    warnings.simplefilter("ignore", category=UserWarning)
    win_io.set_console_position(0, 210, 320, 720)
    return session

def _initialize_hotkeys(session):
    hotkey_to_callback = {
        "numpad_1": lambda *_: mouse_io.get_mouse_pos(),
        "numpad_2": lambda *_: mouse_io.get_mouse_pos(session['client_active'][0]),
        "numpad_3": lambda *_: session.display(),
        "numpad_4": lambda *_: utils.get_DU(session['client_active'][0]),
        "numpad_5": lambda *_: utils.get_wave_count(session['client_active'][0]),
        "numpad_6": lambda *_: utils.get_mob_count(session['client_active'][0]),
        "numpad_7": lambda *_: text_search.extract_text_region_interactive(session['client_active'][0]),
        "numpad_8": lambda *_: utils.extract_image_region_interactive(session['client_active'][0]),
        "numpad_9": lambda *_: utils.compare_until_threshold("du_template", session['client_active'][0], threshold=0.2),
        "numpad_9": lambda *_: keyboard_io.press_and_release("g"),

        "ctrl+up": lambda *_: session['client_active'].calibrate_camera(0, -1),
        "ctrl+down": lambda *_: session['client_active'].calibrate_camera(0, 1),
        "ctrl+left": lambda *_: session['client_active'].calibrate_camera(-1, 0),
        "ctrl+right": lambda *_: session['client_active'].calibrate_camera(1, 0),

        "plus": lambda *_: session.set('keyboard_press_duration', session['keyboard_press_duration'] * 1.01),
        "minus": lambda *_: session.set('keyboard_press_duration', session['keyboard_press_duration'] * 0.99),
        "ctrl+plus": lambda *_: session.set('mouse_delta', session['mouse_delta'] * 10),
        "ctrl+minus": lambda *_: session.set('mouse_delta', session['mouse_delta'] * 0.1),
        
        "alt+up": lambda *_: (print("invoking alt+up"), keyboard_io.press_and_release("w", session['keyboard_press_duration'])),
        "alt+down": lambda *_: (print("invoking alt+down"), keyboard_io.press_and_release("s", session['keyboard_press_duration'])),
        "alt+left": lambda *_: (print("invoking alt+left"), keyboard_io.press_and_release("a", session['keyboard_press_duration'])),
        "alt+right": lambda *_: (print("invoking alt+right"), keyboard_io.press_and_release("d", session['keyboard_press_duration'])),
        
        "shift+numpad_1": lambda *_: session['client_active'].player_coords.get_update(),
        "shift+numpad_2": lambda *_: session['client_active'].cam_rotation.get_update(),
        "shift+numpad_3": lambda *_: session['client_active'].map_data.get_update(),
        "shift+numpad_4": lambda *_: kinematics.rotate_camera(session['client_active'], 0),
        "shift+numpad_5": lambda *_: kinematics.rotate_camera(session['client_active'], 0.5),
        "shift+numpad_6": lambda *_: kinematics.rotate_camera(session['client_active'], 1),
        "shift+numpad_7": lambda *_: kinematics.tilt_camera(session['client_active'], 0),
        "shift+numpad_8": lambda *_: kinematics.tilt_camera(session['client_active'], -0.7),
        "shift+numpad_9": lambda *_: kinematics.tilt_camera(session['client_active'], 0.7),
        "shift+numpad_0": lambda *_: kinematics.rotate(session['client_active'], 0.2, 1),

        "ctrl+numpad_1": lambda *_: session.set('state', LoadingScreen),
        "ctrl+numpad_2": lambda *_: session.set('state', PreBuildPhase),
        "ctrl+numpad_3": lambda *_: session.set('state', BuildPhase),
        "ctrl+numpad_4": lambda *_: session.set('state', CombatPhase),
        "ctrl+numpad_5": lambda *_: session.set('state', PostCombatPhase),
        "ctrl+numpad_6": lambda *_: session.set('state', SummaryScreen),
        "ctrl+numpad_7": lambda *_: keyboard_io.press_and_release("g"),
        "ctrl+numpad_8": lambda *_: pykeyboard.send_keys("g"),
        "ctrl+numpad_9": lambda *_: file_io.save_image(screen_io.capture_window(session['client_active'][0])),
        "ctrl+numpad_0": lambda *_: session.set('state', Idle),

        "f5": lambda *_: win_io.set_focus_console(),
        "ctrl+esc": lambda *_: _keyboard_io.this.EXIT,
    }
    keyboard_io.add_hotkeys(hotkey_to_callback)

def _initialize_session(session):
    # Fetch HWND's
    # clients = sorted(win_io.get_windows(identifier="Dungeon Defenders 2 [#]"), key=lambda tup: tup[1])
    windows = sorted(win_io.get_windows(identifier="Dungeon Defenders 2"), key=lambda tup: tup[1])
    hwnds = [window[0] for window in windows]
    clients = [Client(hwnd, session) for hwnd in hwnds]
    session['clients'] = clients
    session['client_hwnds'] = hwnds
    session['client_count'] = len(clients)
    session['client_active'] = clients[0]
    session['client_main'] = clients[0]
    session['state'] = Idle
    session['wave'] = None
    session['keyboard_press_duration'] = 0.1
    session['mouse_delta'] = 1
    # session.display()

def _initialize_event_hooks(session):
    def _on_win_event(event_type, hwnd, title):
        if hwnd in session['client_hwnds']:
            print(f"Setting active client to: {(hwnd, title[:12])}")
            session['client_active'] = next(c for c in session['clients'] if c.hwnd == hwnd)
    win_io.add_win_event_hook(_on_win_event)

def run(session):
    # status_code = -0x1
    print(f"Execute loop from state: {session['state']}")
    while _keyboard_io.this.status_code != _keyboard_io.this.EXIT:
        cached_state = session['state']
        session['state'] = session['state'].execute(session)
        if session['state'] != cached_state:
            print(f"State change from {cached_state} to {session['state']}.")

        cv2.waitKey(2) & 0xFF


def main():
    session = initialize()
    run(session)
