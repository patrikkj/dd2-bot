import queue
import sys
import threading
from timeit import default_timer as timer

import cv2.cv2 as cv2
import keyboard

# Module level scope pointer
this = sys.modules[__name__]

# Status codes
this.EXIT = 0xF1
this.status_code = None

# Key event queue
this.event_queues = {
    "auto": [{}, queue.SimpleQueue(), True],
    "manual": [{}, queue.SimpleQueue(), True]
}
def threaded_autoflush():
    return_value = None
    while return_value != this.EXIT:
        # try:
        callable_ = this.event_queues['auto'][1].get()
        start = timer()
        return_value = callable_()
        delta = timer() - start
        # except Exception as e:
        #     print(f"ERROR: {e}")
        print(f">>> {return_value}")
        print(f"Exec. time: {delta:.3f}")
    this.status_code = this.EXIT
    sys.exit(0)
threading.Thread(target=threaded_autoflush, daemon=True).start()

# Dictionaries for tracking keyboard input
this.pressed_keys = set()
this.code_to_key = {}
this.key_to_code = {}

# Triggers
this.triggers = {}
this.trigger_output = None
this.is_trigger = False

# Hotkeys
this.is_hotkeys_enabled = True
this.is_suppress_enabled = False
this.is_input_enabled = False
this.suppress_windows = set()


####################
# Initialization
###################
def init():
    # Hook listener callback to all keyboard events
    keyboard.hook(_on_key_event)

    # Conversion from key scan code to corresponding key name
    this.code_to_key = {
        (1, False): "esc",      
        (12, False): "plus",    (53, False): "minus",   (28, False): "enter",   (15, False): "tab",
        (29, False): "ctrl",    (56, False): "alt",     (541, False): "altgr",  (42, False): "shift",   
        (72, False): "up",      (80, False): "down",    (75, False): "left",    (77, False): "right",
        (73, False): "pgup",    (81, False): "pgdn",    (69, False): "pause",
        (59, False): "f1",      (60, False): "f2",      (61, False): "f3",      (62, False): "f4",
        (63, False): "f5",      (64, False): "f6",      (65, False): "f7",      (66, False): "f8",
        (67, False): "f9",      (68, False): "f10",     (87, False): "f11",     (88, False): "f12",
        (79, True): "numpad_1", (80, True): "numpad_2", (81, True): "numpad_3", (75, True): "numpad_4",
        (76, True): "numpad_5", (77, True): "numpad_6", (71, True): "numpad_7", (72, True): "numpad_8",
        (73, True): "numpad_9", (82, True): "numpad_0",
        (53, True): "numpad_divide", (55, True): "numpad_multiply", (78, True): "numpad_plus", 
        (74, True): "numpad_minus",  (28, True): "numpad_enter",    (83, True): "numpad_decimal", 
    }

    # Dictionary of all lower case ascii letters
    _ascii_dict = {(keyboard.key_to_scan_codes(chr(i))[0], False): chr(i) for i in range(97, 123)}
    this.code_to_key.update(_ascii_dict)

    # Dictionary of all numeric characters
    _numeric_dict = {(keyboard.key_to_scan_codes(chr(i))[0], False): chr(i) for i in range(48, 58)}
    this.code_to_key.update(_numeric_dict)

    # Populate dictionary mapping from key to code
    this.key_to_code = {v : k for k, v in this.code_to_key.items()}
###################


def _on_key_event(event):
    # print(vars(event))

    # Break if hotkeys are disabled
    if not this.is_hotkeys_enabled:
        return

    # Register event
    if (event.scan_code, event.is_keypad) not in this.code_to_key:
        # print(f"Key not registered: {event.name} [Code {event.scan_code}, Keypad {event.is_keypad}]")
        return

    # Update set of pressed keys to reflect key status
    if event.event_type == "down":
        this.pressed_keys.add((event.scan_code, event.is_keypad))
    elif (event.scan_code, event.is_keypad) in this.pressed_keys:
        this.pressed_keys.remove((event.scan_code, event.is_keypad))

    # Encode key presses for dictionary lookup
    _pressed_keys = tuple(sorted(this.pressed_keys))

    # If a trigger is set, check if keypress matches
    if this.is_trigger:
        if _pressed_keys in this.triggers:
            this.trigger_output = this.triggers[_pressed_keys]
            return

    # Enqueue action if found
    for _, value in this.event_queues.items():
        # Unpack
        hotkeys, event_queue, is_active = value

        # Continue if queue is inactive
        if not is_active:
            continue

        # Check for trigger
        if _pressed_keys in hotkeys:
            event_queue.put(hotkeys[_pressed_keys])

def set_hotkey_state(suppress=None, hotkeys=None, input_=None):
    """
    Sets hotkey state.
        suppress: Whether to consume key events or not.
        hotkeys: Whether hotkeys should be active or not.
        input_: Whether input dialog is currently active.
    """
    if input_ is True:
        set_hotkey_state(suppress=False, hotkeys=False)
        this.is_input_enabled = True
        return
    elif input_ is False:
        this.is_input_enabled = False
        set_hotkey_state(suppress=False, hotkeys=True)
        return

    # Block any attempts to change hotkey state when input dialog is active
    if this.is_input_enabled:
        return    
    
    if suppress is not None:
        print(f"KeyEvent suppression: {this.is_suppress_enabled} -> {suppress}")
        # # Break if suppression is already set to given value
        # if this.is_suppress_enabled == suppress:
        #     return

        # Rehook key event listener
        keyboard.unhook(_on_key_event)
        keyboard.hook(_on_key_event, suppress=suppress)
        this.is_suppress_enabled = suppress
    
    if hotkeys is not None:
        print(f"Hotkeys active: {this.is_hotkeys_enabled} to {hotkeys}")
        this.is_hotkeys_enabled = hotkeys

# Hotkeys
def add_hotkeys(hotkey_to_callback, event_queue):
    if event_queue in this.event_queues:
        this.event_queues[event_queue][0].update(hotkey_to_callback)
    else:
        this.event_queues[event_queue] = [hotkey_to_callback, [], True]

def remove_hotkeys(hotkey_to_callback, event_queue):
    if event_queue in this.event_queues:
        _dict = this.event_queues[event_queue][0]
        _derived_dict = {k: v for k, v in _dict.items() if k not in hotkey_to_callback}
        this.event_queues[event_queue][0] = _derived_dict

def encode_hotkey(hotkey):
    return tuple(sorted(this.key_to_code[key] for key in hotkey.split("+")))

def encode_hotkeys_dict(dict_):
    return {encode_hotkey(k) : v for k, v in dict_.items()}

def get_hotkeys(event_queue):
    return this.event_queues[event_queue][0] if event_queue in this.event_queues else {}

def unpress_all_keys():
    this.pressed_keys.clear()

def add_suppress_window(hwnd):
    this.suppress_windows.add(hwnd)

def remove_suppress_window(hwnd):
    if hwnd in this.suppress_windows:
        this.suppress_windows.remove(hwnd)

def wait_until_trigger(hotkey_to_output, is_callback):
    this.triggers = hotkey_to_output
    
    # Reset trigger
    this.is_trigger = True
    this.trigger_output = None
    unpress_all_keys()

    # # Rehook event hook
    # _set_key_suppression(True)
    
    # Wait for trigger event
    while this.trigger_output is None:
        cv2.waitKey(1)
    
    # Deactivate triggers
    this.is_trigger = False

    # # Stop key event consumption
    # _set_key_suppression(False)

    # Execute callback if return value is callback, else return value
    if is_callback:
        return this.trigger_output()
    else:
        return this.trigger_output


init()
