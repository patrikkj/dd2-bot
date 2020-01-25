import dd2.io.helpers._screen_io as _screen_io
import dd2.io.helpers._win_io as _win_io


def capture_screen():
    return _screen_io.capture_screen()

def capture_region(x, y, dx, dy, hwnd=None):
    if hwnd:
        _win_io.set_focus(hwnd)
        _x, _y, _, _ = _win_io.get_window_details(hwnd)
        x, y = x + _x, y + _y
    return _screen_io.capture_region(x, y, dx, dy)

def capture_window(hwnd):
    _win_io.set_focus(hwnd)
    x, y, dx, dy = _win_io.get_window_details(hwnd)
    return _screen_io.capture_region(x, y, dx, dy)


# Relative interactive captures
def save_template_interactive(hwnd):
    pass
