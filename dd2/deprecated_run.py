import mouse
import keyboard
import cv2.cv2 as cv2
import platform as _platform

from time import sleep
from mouse._mouse_event import ButtonEvent, MoveEvent, WheelEvent, LEFT, RIGHT, MIDDLE, X, X2, UP, DOWN, DOUBLE

if _platform.system() == 'Windows':
    from mouse import _winmouse as _os_mouse
elif _platform.system() == 'Linux':
    from mouse import _nixmouse as _os_mouse
else:
    raise OSError("Unsupported platform '{}'".format(_platform.system()))

if _platform.system() == 'Windows':
    from keyboard import _winkeyboard as _os_keyboard
elif _platform.system() == 'Linux':
    from keyboard import _nixkeyboard as _os_keyboard
elif _platform.system() == 'Darwin':
    from keyboard import _darwinkeyboard as _os_keyboard
else:
    raise OSError("Unsupported platform '{}'".format(_platform.system()))

from keyboard._keyboard_event import KEY_DOWN, KEY_UP, KeyboardEvent

_callback = None
_x0, _y0 = 0, 0
recording = False
def record(mouse_events, keyboard_events):
    global _callback, recording
    recording = True
    print("Recording")
    mouse_events.clear()
    keyboard_events.clear()

    _callback = mouse.hook(mouse_events.append)
    print("After mouse hook")

    keyboard_events = keyboard.start_recording()
    print("After keyboard hook")
    return _callback


def terminate(mouse_events, keyboard_events):
    global recording
    if not recording:
        return
    recording = False
    print("Terminating")
    mouse.unhook(_callback)
    print("After mouse unhook")
    
    keyboard_events.extend(keyboard.stop_recording())
    print("After keyboard unhook")

    print("\n\n Mouse Events:")
    for e in mouse_events:
        print(e)
    print("\n\n Keyboard Events:")
    for e in keyboard_events:
        print(e)

def calibrate():
    global _x0, _y0
    _x0, _y0 = _os_mouse.get_position()
    print(f"Base pos: ({_x0}, {_y0})")

def play(mouse_events, keyboard_events, speed_factor=1.0, include_clicks=True, include_moves=True, include_wheel=True):
    print("Before play")
    # Mouse
    last_time = None
    state = keyboard.stash_state()

    # x0 = mouse_events[0].x
    # y0 = mouse_events[0].y

    # for i, me in enumerate(mouse_events):
    #     if isinstance(me, MoveEvent):
    #         mouse_events[i] = me._replace(x = me.x - _x0, y = me.y - _y0) 

    events = sorted(mouse_events + keyboard_events, key=lambda e: e.time)
    
    for event in events:
        if speed_factor > 0 and last_time is not None:
            sleep((event.time - last_time) / speed_factor)
        last_time = event.time

        if isinstance(event, ButtonEvent) and include_clicks:
            if event.event_type == UP:
                _os_mouse.release(event.button)
            else:
                _os_mouse.press(event.button)
        elif isinstance(event, MoveEvent) and include_moves:
            print(f"Moving: ({event.x}, {event.y})")
            _x0, _y0 = _os_mouse.get_position()
            # _os_mouse.move_to(event.x, event.y)
            _os_mouse.move_relative(event.x - _x0, event.y - _y0)
        elif isinstance(event, WheelEvent) and include_wheel:
            _os_mouse.wheel(event.delta)
        elif isinstance(event, KeyboardEvent):
            key = event.scan_code or event.name
            keyboard.press(key) if event.event_type == KEY_DOWN else keyboard.release(key)

    keyboard.restore_modifiers(state)
    print("After play")


    # mouse.play(mouse_events)
    # keyboard.play(keyboard_events)

def main():    
    mouse_events = []
    keyboard_events = []

    print("-1")
    keyboard.add_hotkey('F5', record, args=(mouse_events, keyboard_events))    
    keyboard.add_hotkey('F6', terminate, args=(mouse_events, keyboard_events))    
    keyboard.add_hotkey('F7', play, args=(mouse_events, keyboard_events))    
    keyboard.add_hotkey('F8', calibrate, args=())  

    keyboard.add_hotkey('up', _os_mouse.move_relative, args=(0, -30))    
    keyboard.add_hotkey('down', _os_mouse.move_relative, args=(0, 30))    
    keyboard.add_hotkey('left', _os_mouse.move_relative, args=(-30, 0))    
    keyboard.add_hotkey('right', _os_mouse.move_relative, args=(30, 0))    
    
    print("0")
    keyboard.wait('ctrl+shift+q')
    print("After wait")

    # sleep(3)
    # events = mouse.record()
    # print(events)
    # sleep(3)

if __name__ == "__main__":
    main()