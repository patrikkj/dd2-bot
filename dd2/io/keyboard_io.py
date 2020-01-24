import keyboard
import dd2.io.helpers._win_io as _win_io
import dd2.io.helpers._keyboard_io as _keyboard_io


def input_(string):
    _win_io.set_focus_console()
    _keyboard_io._set_hotkey_state(input_=True)
    output = input(string)
    _keyboard_io._set_hotkey_state(input_=False)
    return output

# Keyboard management
def press(key):
    keyboard.press(key)

def release(key):
    keyboard.release(key)

def press_and_release(keys):
    keyboard.press_and_release(keys)

def wait(key):
    keyboard.wait(key)

def write(string):
    keyboard.write(string)


# Key triggers
def wait_until_trigger(hotkey_to_output, is_callback=True):
    return this._wait_until_trigger(this._encode_hotkeys_dict(hotkey_to_output), is_callback)



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
    _keyboard_io.wait_until_trigger(hotkey_to_action)

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
    selected = _keyboard_io.wait_until_trigger(hotkey_to_return_value, is_callback=False)
    # Print selected option
    print(f"Selected: {selected}\n")
    # Return value
    return selected