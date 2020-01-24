import win32api

from dd2.io.misc.singleton import Singleton


class MouseIO(metaclass=Singleton):
    def __init__(self, user_io):
        self.user_io = user_io
    
    # Mouse management
    def get_mouse_pos(self, hwnd=None):
        mouse_pos = win32api.GetCursorPos()
        return self.user_io.win_io.screen_to_client(hwnd, mouse_pos) if hwnd else mouse_pos
