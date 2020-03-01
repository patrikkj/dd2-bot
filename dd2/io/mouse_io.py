
import mouse
import win32api
from mouse import DOUBLE, DOWN, LEFT, MIDDLE, RIGHT, UP, X2, X

import dd2.io as io


# Mouse management
def get_mouse_pos(hwnd=None):
    mouse_pos = win32api.GetCursorPos()
    return io.win.screen_to_client(hwnd, mouse_pos) if hwnd else mouse_pos



# FROM MOUSE API
def is_pressed(button=LEFT):
    return mouse.is_pressed(button=button)

def press(button=LEFT):
    return mouse.press(button=button)

def release(button=LEFT):
    return mouse.release(button=button)

def click(button=LEFT):
    return mouse.click(button=button)

def double_click(button=LEFT):
    return mouse.double_click(button=button)

def right_click():
    return mouse.right_click()

def wheel(delta=1):
    return mouse.wheel(delta=delta)

def move(x, y, absolute=True, duration=0):
    return mouse.move(x, y, absolute=absolute, duration=duration)

def move_click(x, y, absolute=True, duration=0, button=LEFT):
    mouse.move(x, y, absolute=absolute, duration=duration)
    mouse.click(button=button)

def drag(start_x, start_y, end_x, end_y, absolute=True, duration=0):
    return mouse.drag(start_x, start_y, end_x, end_y, absolute=absolute, duration=duration)

def on_button(callback, args=(), buttons=(LEFT, MIDDLE, RIGHT, X, X2), types=(UP, DOWN, DOUBLE)):
    return mouse.on_button(callback, args=args, buttons=buttons, types=types)

def on_click(callback, args=()):
    return mouse.on_click(callback, args=args)

def on_double_click(callback, args=()):
    return mouse.on_double_click(callback, args=args)

def on_right_click(callback, args=()):
    return mouse.on_right_click(callback, args=args)

def on_middle_click(callback, args=()):
    return mouse.on_middle_click(callback, args=args)

def wait(button=LEFT, target_types=(UP, DOWN, DOUBLE)):
    return mouse.wait(button=button, target_types=target_types)

def get_position():
    return mouse.get_position()

def hook(callback):
    return mouse.hook(callback)

def unhook(callback):
    return mouse.unhook(callback)

def unhook_all():
    return mouse.unhook_all()

def record(button=RIGHT, target_types=(DOWN,)):
    return mouse.record(button=button, target_types=target_types)

def play(events, speed_factor=1.0, include_clicks=True, include_moves=True, include_wheel=True):
    return mouse.play(events, speed_factor=speed_factor, include_clicks=include_clicks, include_moves=include_moves, include_wheel=include_wheel)
