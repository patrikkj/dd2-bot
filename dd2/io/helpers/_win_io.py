import ctypes

import pywinauto
import win32api
import win32con
import win32console
import win32gui




# Client / screen conversion
def client_to_screen(hwnd, coords):
    return win32gui.ClientToScreen(hwnd, coords)

def screen_to_client(hwnd, coords):
    return win32gui.ScreenToClient(hwnd, coords)

# Windows API
def get_console():
    return win32console.GetConsoleWindow()

def set_focus(hwnd, foreground=True):
    app = pywinauto.application.Application().connect(handle=hwnd)
    window = app.window(handle=hwnd)
    window.set_focus()
    if foreground:
        win32gui.SetForegroundWindow(hwnd)

def set_mouse_capture(hwnd):
    win32gui.SetCapture(hwnd)

def get_hwnds(filter_=lambda title: True):
    windows = []
    win32gui.EnumWindows(lambda hwnd, windows: windows.append((hwnd, win32gui.GetWindowText(hwnd))), windows)
    return [hwnd for hwnd, title in windows if filter_(title)]

def get_windows(filter_=lambda title: True):
    windows = []
    win32gui.EnumWindows(lambda hwnd, windows: windows.append((hwnd, win32gui.GetWindowText(hwnd))), windows)
    return [(hwnd, title) for hwnd, title in windows if filter_(title)]

def get_child_windows(parent_hwnd, filter_=lambda title: True):
    children = []
    win32gui.EnumChildWindows(parent_hwnd, lambda hwnd, children: children.append((hwnd, win32gui.GetWindowText(hwnd))), children)
    return [(hwnd, title) for hwnd, title in children if filter_(title)]

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def get_focused_window():
    return win32gui.GetForegroundWindow()

def get_window_title(hwnd):
    return win32gui.GetWindowText(hwnd)

def get_screen_resolution():
    width = win32api.GetSystemMetrics(0)
    height = win32api.GetSystemMetrics(1)
    return width, height


# Window details
def get_window_details(hwnd):
    x, y = client_to_screen(hwnd, (0, 0))
    _, _, dx, dy = win32gui.GetClientRect(hwnd)
    return x, y, dx, dy

def set_window_details(hwnd, x=-1, y=-1, dx=-1, dy=-1, on_top=True):
    _x, _y, _dx, _dy = get_window_details(hwnd)
    x = x if x != -1 else _x
    y = y if y != -1 else _y
    dx = dx if dx != -1 else _dx
    dy = dy if dy != -1 else _dy
    pos_flag = win32con.HWND_TOPMOST if on_top else win32con.HWND_TOP
    win32gui.SetWindowPos(hwnd, pos_flag, x, y, dx - 1, dy - 1, 32)
    win32gui.SetWindowPos(hwnd, pos_flag, x, y, dx, dy, 32)


# def get_modified_res(hwnd):
#     rect = win32gui.GetWindowRect(hwnd)
#     clientRect = win32gui.GetClientRect(hwnd)
#     windowOffset = math.floor(((rect[2]-rect[0])-clientRect[2])/2)
#     titleOffset = ((rect[3]-rect[1])-clientRect[3]) - windowOffset
#     newRect = (rect[0]+windowOffset, rect[1]+titleOffset, rect[2]-windowOffset, rect[3]-windowOffset)
#     return newRect
