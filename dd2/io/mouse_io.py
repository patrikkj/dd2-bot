import win32api
import pyautogui
from dd2.io.singleton import Singleton

class MouseIO(metaclass=Singleton):
    def __init__(self, user_io):
        self.user_io = user_io

    
    # Mouse management
    def get_mouse_pos(self, hwnd=None):
        mouse_pos = win32api.GetCursorPos()
        return self.user_io.win_io.screen_to_client(hwnd, mouse_pos) if hwnd else mouse_pos


# # Map management
# def move_left():
#     pyautogui.click(x=340, y=500)

# def move_right():
#     pyautogui.click(x=1594, y=500)

# def move_up():
#     pyautogui.click(x=1031, y=29)

# def move_down():
#     pyautogui.click(x=1004, y=923)
