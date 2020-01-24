import time
import warnings
from enum import Enum, auto

import cv2.cv2 as cv2

from . import session as sess
from .io.user_io import keyboard_io, mouse_io, user_io, win_io
from .state import (BuildPhase, CombatPhase, Idle, LoadingScreen,
                    PostCombatPhase, PreBuildPhase, SummaryScreen)
from .utils import image_search, text_search, utils

# Status codes
EXIT = 0x00


def initialize():
    state = Idle
    session = sess.get()

    _initialize_session(session)
    _initialize_hotkeys(session)

    warnings.simplefilter("ignore", category=UserWarning)
    win_io.set_client_position(win_io.get_console(), 0, 210, 380, 720)
    return state, session

def _initialize_hotkeys(session):
    hotkey_to_callback = {
        "f5": lambda *_: text_search.extract_text_region_interactive_screen(),
        "f6": lambda *_: print(mouse_io.get_mouse_pos()),
        "f7": lambda *_: print(win_io.screen_to_client(session['client_active'][0], mouse_io.get_mouse_pos())),
        "f8": lambda *_: print(utils.get_DU(session['client_active'][0])),
        "f9": lambda *_: print(utils.get_wave_count(session['client_active'][0])),
        "f10": lambda *_: print(utils.get_mob_count(session['client_active'][0])),
        "ctrl+1": lambda *_: print(mouse_io.get_mouse_pos()),
        "ctrl+esc": lambda *_: (print("EXIT"), EXIT)[1]
    }
    keyboard_io.add_hotkeys(hotkey_to_callback)

def _initialize_session(session):
    # Fetch HWND's
    clients = sorted(win_io.get_windows(identifier="Dungeon Defenders 2 [#]"))
    session['clients'] = clients
    session['client_hwnds'] = [client[0] for client in clients]
    session['client_count'] = len(clients)
    session['client_active'] = clients[0]
    session.display()

def run(state, session):
    status_code = -0x1
    while status_code not in (EXIT, ):
        # Execute currently active state
        # print(f"State: {state}")
        state = state.execute(session)

        # Perform enqueued actions
        while user_io.has_events("default") and (status_code not in (EXIT, )):
            status_code = user_io.call_next("default", tuple())
            # print(f"Status code: {status_code}")
        cv2.waitKey(2) & 0xFF


def main():
    state, session = initialize()
    run(state, session)
