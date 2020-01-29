import ctypes
import ctypes.wintypes

import win32con

user32 = ctypes.windll.user32

WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)

eventTypes = {
    win32con.EVENT_OBJECT_FOCUS: "Focus"
}

def _callable_wrapper(callable_):
    """
    Returns a wrapped WinEventHook callback function, calling the inner function.

    Arguments for inner function:
        event_type: Type of event
        hwnd: Window handle
        title: Window title
    """
    # print("Creating callback")
    def _callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        nonlocal callable_
        length = user32.GetWindowTextLengthW(hwnd)
        title = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, title, length + 1)
        # print("Running _callback")
        # Execute inner function
        callable_(eventTypes.get(event, hex(event)), hwnd, title.value)
    return _callback

def add_event_hook(callable_, event_type=win32con.EVENT_OBJECT_FOCUS):
    '''
    Hooks the callable function to a windows event hook. 
    Inner function is called for every change in window state of the specified type. 

    Arguments for inner function:
        event_type: Type of event
        hwnd: Window handle
        title: Window title
    '''
    WinEventProc = WinEventProcType(_callable_wrapper(callable_))
    user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
    hook_id = user32.SetWinEventHook(
        event_type,
        event_type,
        0,
        WinEventProc,
        0,
        0,
        win32con.WINEVENT_OUTOFCONTEXT
    )
    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessageW(msg)
        user32.DispatchMessageW(msg)

    user32.UnhookWinEvent(hook_id)

def main():
    add_event_hook(lambda *_:print(_))

if __name__ == '__main__':
    main()
