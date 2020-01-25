import dd2.io.helpers._win_io as _win_io
import win32api


# Mouse management
def get_mouse_pos(hwnd=None):
    mouse_pos = win32api.GetCursorPos()
    return _win_io.screen_to_client(hwnd, mouse_pos) if hwnd else mouse_pos
