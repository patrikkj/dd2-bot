import keyboard
import time
import dd2.io.helpers._win_io as _win_io

from dd2.io.helpers import _file_io, _keyboard_io, _mouse_io, _screen_io, _win_io

def input_(string):
    _win_io.set_focus(_win_io.get_console())
    _keyboard_io.set_hotkey_state(input_=True)
    output = input(string)
    _keyboard_io.set_hotkey_state(input_=False)
    return output

# Keyboard management
def press(key):
    keyboard.press(key)

def release(key):
    keyboard.release(key)

def press_and_release(keys, duration=0):
    keyboard.press(keys)
    if duration:
        time.sleep(duration)
    keyboard.release(keys)

def send(keys):
    keyboard.send(keys)

def wait(key):
    keyboard.wait(key)

def write(string):
    keyboard.write(string)


# Hotkeys
def add_hotkeys(hotkey_to_callback, event_queue="auto"):
    return _keyboard_io.add_hotkeys(_keyboard_io.encode_hotkeys_dict(hotkey_to_callback), event_queue)

def remove_hotkeys(hotkey_to_callback, event_queue="auto"):
    return _keyboard_io.remove_hotkeys(_keyboard_io.encode_hotkeys_dict(hotkey_to_callback), event_queue)


# Key triggers
def wait_until_trigger(hotkey_to_output, is_callback=True):
    return _keyboard_io.wait_until_trigger(_keyboard_io.encode_hotkeys_dict(hotkey_to_output), is_callback)


# Print operations
def select_from_menu(menu_dict, title=None, default=None):
    print("\n")
    # Print title if requested
    if title:
        print(f"--- {title} --- ")
    # Print menu options
    hotkey_to_action = {}
    for num, entry in enumerate(menu_dict.items(), 1):
        option, action = entry
        print(f"  [{num}] - {option}")
        hotkey_to_action[f"ctrl+{num}"] = action
    # Set default selection
    if default:
        hotkey_to_action["enter"] = list(menu_dict.values())[default - 1]
    # Wait for user input
    print("\nSelect using [Ctrl] + [0-9] ...")
    #Adding triggers
    wait_until_trigger(hotkey_to_action)

def select_from_options(options_dict, title=None, default=None):
    if title:
        print(f"\n - {title} - ")
    # Print menu options
    hotkey_to_return_value = {}
    for num, entry in enumerate(options_dict.items(), 1):
        option, return_value = entry
        print(f"  [{num}] - {option}")
        hotkey_to_return_value[f"ctrl+{num}"] = return_value
    # Add default selection
    if default:
        hotkey_to_return_value["enter"] = list(options_dict.values())[default - 1]
    # Wait for user input
    print("\nSelect using [Ctrl] + [0-9] ...")
    #Adding triggers
    selected = wait_until_trigger(hotkey_to_return_value, is_callback=False)
    # Print selected option
    print(f"Selected: {selected}\n")
    # Return value
    return selectedremove_hotkeys