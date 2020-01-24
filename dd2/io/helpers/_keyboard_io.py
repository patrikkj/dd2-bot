import keyboard
import threading
import cv2.cv2 as cv2
from .singleton import Singleton
from queue import SimpleQueue


# Module level scope pointer
import sys
this = sys.modules[__name__]

# Key event queue
this.event_queues = {
    "auto": [{}, SimpleQueue(), True],
    "manual": [{}, SimpleQueue(), True]
}
def threaded_autoflush():
    while True:
        item = q.get()
        if item is None:
            break
        do_work(item)
        q.task_done()

threading.Thread(target = winevent.add_event_hook, args = (self._on_win_event, )).start()


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

# Hook listener callback to all keyboard events
keyboard.hook(this._on_key_event)

# Conversion from key scan code to corresponding key name
this.code_to_key = {
    1: "esc",12: "plus", 53: "minus", 28: "enter", 
    29: "ctrl", 56: "alt", 42: "shift",
    72: "up", 80: "down", 75: "left", 77: "right",
    59: "f1", 60: "f2", 61: "f3", 62: "f4",
    63: "f5", 64: "f6", 65: "f7", 66: "f8",
    67: "f9", 68: "f10", 87: "f11", 88: "f12"
}

# Dictionary of all lower case ascii letters
_ascii_dict = {keyboard.key_to_scan_codes(chr(i))[0]: chr(i) for i in range(97, 123)}
this.code_to_key.update(_ascii_dict)

# Dictionary of all numeric characters
_numeric_dict = {keyboard.key_to_scan_codes(chr(i))[0]: chr(i) for i in range(48, 58)}
this.code_to_key.update(_numeric_dict)

# Populate dictionary mapping from key to code
this.key_to_code = {v : k for k, v in this.code_to_key.items()}

###################



def _on_key_event(event):
    # Break if hotkeys are disabled
    if not this.is_hotkeys_enabled:
        return

    # Register event
    if event.scan_code not in this.code_to_key:
        print(f"Key not registered: {event.name} [Code {event.scan_code}]")
        return

    # Update set of pressed keys to reflect key status
    if event.event_type == "down":
        this.pressed_keys.add(event.scan_code)
    elif event.scan_code in this.pressed_keys:
        this.pressed_keys.remove(event.scan_code)

    # Encode key presses for dictionary lookup
    _pressed_keys = tuple(sorted(this.pressed_keys))

    # If a trigger is set, check if keypress matches
    if this.is_trigger:
        if _pressed_keys in this.triggers:
            this.trigger_output = this.triggers[_pressed_keys]
            return

    # Enqueue action if found
    for _, value in this.user_io.event_queues.items():
        # Unpack
        hotkeys, event_queue, is_active = value

        # Continue if queue is inactive
        if not is_active:
            continue

        # Check for trigger
        if _pressed_keys in hotkeys:
            event_queue.append(hotkeys[_pressed_keys])

def _set_hotkey_state(suppress=None, hotkeys=None, input_=None):
    """
    Sets hotkey state.
        suppress: Whether to consume key events or not.
        hotkeys: Whether hotkeys should be active or not.
        input_: Whether input dialog is currently active.
    """
    if input_ is True:
        this._set_hotkey_state(suppress=False, hotkeys=False)
        this.is_input_enabled = True
        return
    elif input_ is False:
        this.is_input_enabled = False
        this._set_hotkey_state(suppress=True, hotkeys=True)
        return

    # Block any attempts to change hotkey state when input dialog is active
    if this.is_input_enabled:
        return    
    
    if suppress is not None:
        print(f"Setting suppression from {this.is_suppress_enabled} to {suppress}")
        # Break if suppression is already set to given value
        if this.is_suppress_enabled == suppress:
            return

        # Rehook key event listener
        keyboard.unhook(this._on_key_event)
        keyboard.hook(this._on_key_event, suppress=suppress)
        this.is_suppress_enabled = suppress
    
    if hotkeys is not None:
        print(f"Setting hotkey from {this.is_hotkeys_enabled} to {hotkeys}")
        this.is_hotkeys_enabled = hotkeys

# Hotkeys
def _add_hotkeys(hotkey_to_callback, event_queue):
    if event_queue in this.user_io.event_queues:
        this.user_io.event_queues[event_queue][0].update(hotkey_to_callback)
    else:
        this.user_io.event_queues[event_queue] = [hotkey_to_callback, [], True]

def _remove_hotkeys(hotkey_to_callback, event_queue):
    if event_queue in this.user_io.event_queues:
        _dict = this.user_io.event_queues[event_queue][0]
        _derived_dict = {k: v for k, v in _dict.items() if k not in hotkey_to_callback}
        this.user_io.event_queues[event_queue][0] = _derived_dict

def _encode_hotkey(hotkey):
    return tuple(sorted(this.key_to_code[key] for key in hotkey.split("+")))

def _encode_hotkeys_dict(dict_):
    return {this._encode_hotkey(k) : v for k, v in dict_.items()}

def get_hotkeys(event_queue):
    return this.user_io.event_queues[event_queue][0] if event_queue in this.user_io.event_queues else {}

def add_hotkeys(hotkey_to_callback, event_queue="default"):
    return this._add_hotkeys(this._encode_hotkeys_dict(hotkey_to_callback), event_queue)

def remove_hotkeys(hotkey_to_callback, event_queue="default"):
    return this._remove_hotkeys(this._encode_hotkeys_dict(hotkey_to_callback), event_queue)

def unpress_all_keys(self):
    this.pressed_keys.clear()

def add_suppress_window(hwnd):
    this.suppress_windows.add(hwnd)

def remove_suppress_window(hwnd):
    if hwnd in this.suppress_windows:
        this.suppress_windows.remove(hwnd)

def _wait_until_trigger(hotkey_to_output, is_callback):
    this.triggers = hotkey_to_output
    
    # Reset trigger
    this.is_trigger = True
    this.trigger_output = None
    this.unpress_all_keys()

    # # Rehook event hook
    # this._set_key_suppression(True)
    
    # Wait for trigger event
    while this.trigger_output is None:
        cv2.waitKey(1)
    
    # Deactivate triggers
    this.is_trigger = False

    # # Stop key event consumption
    # this._set_key_suppression(False)

    # Execute callback if return value is callback, else return value
    if is_callback:
        return this.trigger_output()
    else:
        return this.trigger_output
