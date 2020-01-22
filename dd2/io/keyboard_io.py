import keyboard
import cv2.cv2 as cv2
from dd2.io.singleton import Singleton


class KeyboardIO(metaclass=Singleton):
    # Dictionaries for tracking keyboard input
    pressed_keys = set()
    code_to_key = {}
    key_to_code = {}

    # Triggers
    triggers = {}
    trigger_output = None
    is_trigger = False

    # Hotkeys
    is_hotkeys_enabled = False
    is_suppress_enabled = False
    is_input_enabled = False
    suppress_windows = set()
    
    def __init__(self, user_io):
        self.user_io = user_io
        # Hook listener callback to all keyboard events
        keyboard.hook(self._on_key_event)


    def _initialize_hotkeys(self):
        # Conversion from key scan code to corresponding key name
        self.code_to_key = {
            1: "esc",12: "plus", 53: "minus", 28: "enter", 
            29: "ctrl", 56: "alt", 42: "shift",
            72: "up", 80: "down", 75: "left", 77: "right",
        }

        # Dictionary of all lower case ascii letters
        ascii_dict = {keyboard.key_to_scan_codes(chr(i))[0]: chr(i) for i in range(97, 123)}
        self.code_to_key.update(ascii_dict)
        
        # Dictionary of all numeric characters
        numeric_dict = {keyboard.key_to_scan_codes(chr(i))[0]: chr(i) for i in range(48, 58)}
        self.code_to_key.update(numeric_dict)

        # Populate dictionary mapping from key to code
        self.key_to_code = {v : k for k, v in self.code_to_key.items()}

    def _on_key_event(self, event):
        # Break if hotkeys are disabled
        if not self.is_hotkeys_enabled:
            return

        # Register event
        if event.scan_code not in self.code_to_key:
            return

        # Update set of pressed keys to reflect key status
        if event.event_type == "down":
            self.pressed_keys.add(event.scan_code)
        elif event.scan_code in self.pressed_keys:
            self.pressed_keys.remove(event.scan_code)

        # Encode key presses for dictionary lookup
        _pressed_keys = tuple(sorted(self.pressed_keys))

        # Debugging
        # print("\n - Key event - ")
        # print(f"  Key: {event.name}")
        # print(f"  Status: {event.event_type}")
        # print(f"  Trigger: {self.is_trigger}")
        # print(f"  Pressed keys: {_pressed_keys}")

        # If a trigger is set, check if keypress matches
        if self.is_trigger:
            if _pressed_keys in self.triggers:
                # print(f"Pressed: {pressed_keys}\nTriggers: {self.triggers}")
                self.trigger_output = self.triggers[_pressed_keys]
                # print(f"Trigger output: {self.trigger_output}")
                return

        # Enqueue action if found
        for _, value in self.event_queues.items():
            # Unpack
            hotkeys, event_queue, is_active = value

            # Continue if queue is inactive
            if not is_active:
                continue

            # Check for trigger
            if _pressed_keys in hotkeys:
                event_queue.append(hotkeys[_pressed_keys])

    def _set_hotkey_state(self, suppress=None, hotkeys=None, input_=None):
        """
        Sets hotkey state.
            suppress: Whether to consume key events or not.
            hotkeys: Whether hotkeys should be active or not.
            input_: Whether input dialog is currently active.
        """
        if input_ is True:
            self._set_hotkey_state(suppress=False, hotkeys=False)
            self.is_input_enabled = True
            return
        elif input_ is False:
            self.is_input_enabled = False
            self._set_hotkey_state(suppress=True, hotkeys=True)
            return

        # Block any attempts to change hotkey state when input dialog is active
        if self.is_input_enabled:
            return    
        
        if suppress is not None:
            print(f"Setting suppression from {self.is_suppress_enabled} to {suppress}")
            # Break if suppression is already set to given value
            if self.is_suppress_enabled == suppress:
                return

            # Rehook key event listener
            keyboard.unhook(self._on_key_event)
            keyboard.hook(self._on_key_event, suppress=suppress)
            self.is_suppress_enabled = suppress
        
        if hotkeys is not None:
            print(f"Setting hotkey from {self.is_hotkeys_enabled} to {hotkeys}")
            self.is_hotkeys_enabled = hotkeys

    # Hotkeys
    def _add_hotkeys(self, hotkey_to_callback, event_queue):
        if event_queue in self.event_queues:
            self.event_queues[event_queue][0].update(hotkey_to_callback)
        else:
            self.event_queues[event_queue] = [hotkey_to_callback, [], True]

    def _remove_hotkeys(self, hotkey_to_callback, event_queue):
        if event_queue in self.event_queues:
            _dict = self.event_queues[event_queue][0]
            _derived_dict = {k: v for k, v in _dict.items() if k not in hotkey_to_callback}
            self.event_queues[event_queue][0] = _derived_dict

    def _encode_hotkey(self, hotkey):
        return tuple(sorted(self.key_to_code[key] for key in hotkey.split("+")))

    def _encode_hotkeys_dict(self, dict_):
        return {self._encode_hotkey(k) : v for k, v in dict_.items()}

    def get_hotkeys(self, event_queue):
        return self.event_queues[event_queue][0] if event_queue in self.event_queues else {}

    def add_hotkeys(self, hotkey_to_callback, event_queue="default"):
        return self._add_hotkeys(self._encode_hotkeys_dict(hotkey_to_callback), event_queue)

    def remove_hotkeys(self, hotkey_to_callback, event_queue="default"):
        return self._remove_hotkeys(self._encode_hotkeys_dict(hotkey_to_callback), event_queue)

    def unpress_all_keys(self):
        self.pressed_keys.clear()

    def add_suppress_window(self, hwnd):
        self.suppress_windows.add(hwnd)

    def remove_suppress_window(self, hwnd):
        if hwnd in self.suppress_windows:
            self.suppress_windows.remove(hwnd)

    def _wait_until_trigger(self, hotkey_to_output, is_callback):
        self.triggers = hotkey_to_output
        
        # Reset trigger
        self.is_trigger = True
        self.trigger_output = None
        self.unpress_all_keys()

        # # Rehook event hook
        # self._set_key_suppression(True)
        
        # Wait for trigger event
        while self.trigger_output is None:
            cv2.waitKey(1)
        
        # Deactivate triggers
        self.is_trigger = False

        # # Stop key event consumption
        # self._set_key_suppression(False)

        # Execute callback if return value is callback, else return value
        if is_callback:
            return self.trigger_output()
        else:
            return self.trigger_output

    def wait_until_trigger(self, hotkey_to_output, is_callback=True):
        return self._wait_until_trigger(self._encode_hotkeys_dict(hotkey_to_output), is_callback)


    # Print operations
    def select_from_menu(self, menu_dict, title=None, default=None):
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
        # print(f"Adding triggers: {hotkey_to_action}")
        self.wait_until_trigger(hotkey_to_action)
        
        # keyboard.stash_state()
        # keypress = keyboard.get_hotkey_name()
        # while keypress not in hotkey_to_action.keys():
        #     keypress = keyboard.get_hotkey_name()
        # keyboard.stash_state()

        # # Print selected option
        # selected = f"Default option ({default})" if keypress == "enter" else keypress.split('+')[1]
        # print(f"Selected: {selected}\n")

        # # Perform action
        # hotkey_to_action[keypress]()

    def select_from_options(self, options_dict, title=None, default=None):
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
        selected = self.wait_until_trigger(hotkey_to_return_value, is_callback=False)

        # Print selected option
        # selected_print = f"Default option ({default}" if keypress == "enter" else keypress.split('+')[1]
        print(f"Selected: {selected}\n")

        # Return value
        return selected
        # return hotkey_to_return_value[keypress]
    
    def input_(self, string):
        utils.set_focus_console()
        self._set_hotkey_state(input_=True)
        output = input(string)
        self._set_hotkey_state(input_=False)
        return output

    # Keyboard management
    @staticmethod
    def press(key):
        keyboard.press(key)

    @staticmethod
    def release(key):
        keyboard.release(key)

    @staticmethod
    def press_and_release(keys):
        keyboard.press_and_release(keys)

    @staticmethod
    def wait(key):
        keyboard.wait(key)

    @staticmethod
    def write(string):
        keyboard.write(string)