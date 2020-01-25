
import time
import dd2.io.helpers._win_io as _win_io


# Client / screen conversion
def client_to_screen(hwnd, coords):
    return _win_io.client_to_screen(hwnd, coords)

def screen_to_client(hwnd, coords):
    return _win_io.screen_to_client(hwnd, coords)


# Window API
def set_focus_console():
    _win_io.set_focus(_win_io.get_console())

def get_windows(identifier=""):
    return _win_io.get_windows(filter=lambda title: identifier in title)

def get_child_windows(parent_hwnd, identifier=""):
    return _win_io.get_child_windows(parent_hwnd, filter=lambda title: identifier in title)


# Loops
def ensure_window_exists(identifier):
    windows = _win_io.get_windows(identifier)
    while not windows:
        time.sleep(0.1)
        windows = _win_io.get_windows(identifier)
    return windows[0]
