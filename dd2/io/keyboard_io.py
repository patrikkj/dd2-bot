import time

import keyboard

import dd2.core.services as services

from .helpers import _keyboard_io, _win_io


# Keyboard management
def press(key):
    # print(f"Press '{key}' ({time.time()%1000:.5f})")
    keyboard.press(key)

def release(key):
    # print(f"Release '{key}' ({time.time()%1000:.5f})")
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

def is_pressed(key):
    return keyboard.is_pressed(key)

def stash_state():
    return keyboard.stash_state()


# Movement injection
def create_service(client):
    return services.keyboard_service.create_service(client)

def kill_service(client):
    return services.keyboard_service.kill_service(client)

def set_input_vector(client, input_vector):
    return services.keyboard_service.set_input_vector(client, input_vector)

def set_input_x(client, input_x):
    return services.keyboard_service.set_input_x(client, input_x)

def set_input_y(client, input_y):
    return services.keyboard_service.set_input_y(client, input_y)


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
        hotkey_to_return_value[f"ctrl+numpad_{num}"] = return_value
    # Add default selection
    if default:
        hotkey_to_return_value["enter"] = list(options_dict.values())[default - 1]
    # Wait for user input
    print("\nSelect using [Ctrl] + Numpad[1-9] ...")
    #Adding triggers
    selected = wait_until_trigger(hotkey_to_return_value, is_callback=False)
    # Print selected option
    # print(f"Selected: {selected}\n")
    # Return value
    return selected

def select_from_options_input(options_dict, title=None):
    if title:
        print(f"\n - {title} - ")
    # Print menu options
    num_to_return_value = {}
    for num, entry in enumerate(options_dict.items(), 1):
        option, return_value = entry
        print(f"  [{num}] - {option}")
        num_to_return_value[num] = return_value
        
    # Wait for user input
    while True:
        try:    
            user_input = input_("\nSelect option: ")
            selected = num_to_return_value[int(user_input)]
            break
        except Exception as e:
            print(e)
    # Print selected option
    # print(f"Selected: {selected}\n")
    
    # Return value
    return selected

def input_(string):
    focused_hwnd = _win_io.get_focused_window()
    _win_io.set_focus(_win_io.get_console())
    _keyboard_io.set_hotkey_state(input_=True)
    output = input(string)
    _keyboard_io.set_hotkey_state(input_=False)
    _win_io.set_focus(focused_hwnd)
    return output
