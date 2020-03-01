
import time
import threading
from .helpers import _win_io, _winevent


def add_win_event_hook(callable_):
    '''Callable of type (event_type, hwnd, title) -> ...'''
    # Hook listener callback to all window events on separate thread
    threading.Thread(target=_winevent.add_event_hook, args=(callable_, )).start()


# Client / screen conversion
def client_to_screen(hwnd, coords):
    return _win_io.client_to_screen(hwnd, coords)

def screen_to_client(hwnd, coords):
    return _win_io.screen_to_client(hwnd, coords)


# Window API
def set_focus(hwnd, foreground=True):
    _win_io.set_focus(hwnd, foreground=foreground)

def set_focus_console():
    _win_io.set_focus(_win_io.get_console())

def set_mouse_capture(hwnd):
    _win_io.set_mouse_capture(hwnd)

def set_console_position(x, y, dx, dy):
    return _win_io.set_window_details(_win_io.get_console(), x, y, dx, dy)

def get_window_title(hwnd):
    return _win_io.get_window_title(hwnd)

def get_focused_window():
    return _win_io.get_focused_window()

def get_hwnds(identifier=""):
    return _win_io.get_hwnds(filter_=lambda title: identifier in title)

def get_windows(identifier=""):
    return _win_io.get_windows(filter_=lambda title: identifier in title)

def get_child_windows(parent_hwnd, identifier=""):
    return _win_io.get_child_windows(parent_hwnd, filter_=lambda title: identifier in title)



# Loops
def ensure_window_exists(identifier):
    windows = _win_io.get_windows(identifier)
    while not windows:
        time.sleep(0.1)
        windows = _win_io.get_windows(identifier)
    return windows[0]
