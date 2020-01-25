import win32api


# Mouse management
def get_mouse_pos():
    return win32api.GetCursorPos()
