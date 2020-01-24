import ctypes
import time
import math

import threading
import win32api
import win32con
import win32console
import win32gui
import pywinauto

# from pywinauto import Application
from PIL import ImageGrab
from . import winevent
from .singleton import Singleton



class WinIO(metaclass=Singleton):
    def __init__(self, user_io):
        self.user_io = user_io
        # Hook listener callback to all window events on separate thread
        # threading.Thread(target = winevent.add_event_hook, args = (self._on_win_event, )).start()


    def _on_win_event(self, event_type, hwnd, title):
        print("Firing win event")
        if hwnd in self.user_io.keyboard_io.suppress_windows:
            self.user_io.keyboard_io._set_hotkey_state(suppress=True, hotkeys=True)
        else:
            self.user_io.keyboard_io._set_hotkey_state(suppress=False, hotkeys=False)


    # Client / screen conversion
    @staticmethod
    def client_to_screen(hwnd, coords):
        return win32gui.ClientToScreen(hwnd, coords)

    @staticmethod
    def screen_to_client(hwnd, coords):
        return win32gui.ScreenToClient(hwnd, coords)


    # Screen capturing
    @staticmethod
    def capture_screen():
        return ImageGrab.grab()

    @staticmethod
    def capture_region(x, y, dx, dy, hwnd=None):
        if hwnd:
            WinIO.set_focus(hwnd)
            _x, _y = WinIO.get_client_position(hwnd)
            x, y = x + _x, y + _y
        return ImageGrab.grab(bbox=(x, y, x + dx, y + dy))

    @staticmethod
    def capture_window(hwnd):
        WinIO.set_focus(hwnd)
        x, y = WinIO.get_client_position(hwnd)
        dx, dy = WinIO.get_client_resolution(hwnd)
        return WinIO.capture_region(x, y, dx, dy)

    # Windows API
    @staticmethod
    def _get_windows(filter=lambda title: True):
        windows = []
        win32gui.EnumWindows(lambda hwnd, windows: windows.append((hwnd, win32gui.GetWindowText(hwnd))), windows)
        return [(hwnd, title) for hwnd, title in windows if filter(title)]

    @staticmethod
    def get_windows(identifier=""):
        return WinIO._get_windows(filter=lambda title: identifier in title)

    @staticmethod
    def get_window(identifier):
        windows = []
        win32gui.EnumWindows(lambda hwnd, windows: windows.append((hwnd, win32gui.GetWindowText(hwnd))), windows)
        
        # Search for window
        for hwnd, title in windows:
            if identifier in title:
                return (hwnd, title)
        return None

    @staticmethod
    def get_windows_count(identifier):
        return len(WinIO.get_windows(identifier))

    @staticmethod
    def _get_child_windows(parent_hwnd, filter=lambda title: True):
        children = []
        win32gui.EnumChildWindows(WinIO.get_console(), lambda hwnd, children: children.append((hwnd, win32gui.GetWindowText(hwnd))), children)
        return [(hwnd, title) for hwnd, title in children if filter(title)]

    @staticmethod
    def get_child_windows(parent_hwnd, identifier=""):
        return WinIO._get_child_windows(parent_hwnd, filter=lambda title: identifier in title)

    @staticmethod
    def get_console():
        return win32console.GetConsoleWindow()

    @staticmethod
    def set_focus(hwnd):
        app = pywinauto.application.Application().connect(handle=hwnd)
        window = app.window(handle=hwnd)
        window.set_focus()

    @staticmethod
    def set_focus_console():
        WinIO.set_focus(WinIO.get_console())

    @staticmethod
    def set_console_position(x, y, dx, dy, on_top=True):
        pos_flag = win32con.HWND_TOPMOST if on_top else win32con.HWND_TOP
        win32gui.SetWindowPos(win32console.GetConsoleWindow(), pos_flag, x, y, dx, dy, 0)
        # fra 59
        # ned til 1039

    @staticmethod
    def set_title(title):
        ctypes.windll.kernel32.SetConsoleTitleW(title)

    @staticmethod
    def get_screen_resolution():
        width = win32api.GetSystemMetrics(0)
        height = win32api.GetSystemMetrics(1)
        return width, height
    
    @staticmethod
    def get_modified_res(hwnd):
        rect = win32gui.GetWindowRect(hwnd)
        clientRect = win32gui.GetClientRect(hwnd)
        windowOffset = math.floor(((rect[2]-rect[0])-clientRect[2])/2)
        titleOffset = ((rect[3]-rect[1])-clientRect[3]) - windowOffset
        newRect = (rect[0]+windowOffset, rect[1]+titleOffset, rect[2]-windowOffset, rect[3]-windowOffset)
        return newRect

    @staticmethod
    def get_client_resolution(hwnd):
        _, _, right, bottom = win32gui.GetClientRect(hwnd)
        return right, bottom

    @staticmethod
    def get_client_position(hwnd):
        return WinIO.client_to_screen(hwnd, (0, 0))

    @staticmethod
    def set_client_resolution(hwnd, width, height):
        WinIO.set_focus(hwnd)
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        # win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, left, top, width, height, 32)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, left, top, width - 1, height - 1, 32)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, left, top, width, height, 32)

    @staticmethod
    def set_client_position(hwnd, x, y, width=-1, height=-1):
        WinIO.set_focus(hwnd)
        # win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, width, height, 32)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, width - 1, height - 1, 32)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, width, height, 32)

    @staticmethod
    def ensure_window_exists(identifier):
        window = WinIO.get_window(identifier)
        while window is None:
            time.sleep(0.1)
            window = WinIO.get_window(identifier)
        return window

    @staticmethod
    def ensure_window_exists_count(identifier, count):
        windows_count = WinIO.get_windows_count(identifier)
        while windows_count != count:
            time.sleep(0.1)
            windows_count = WinIO.get_windows_count(identifier)



