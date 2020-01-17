import argparse
import warnings

import botofus.session as sess
import botofus.app.capture as capture
import botofus.app.helpers.text_search as text_search
import botofus.utils.utils as utils
import botofus.models.text_record as text_record
from botofus.utils.userio import UserIO


class Client():
    def __init__(self, args):
        self.args = args
        
        # Connect to active session
        session = sess.get()
        session.pair_client(self, self.args["gameclient_hwnd"])

        # Set instance variables
        gameclient_hwnd = self.args["gameclient_hwnd"]
        self.userio = UserIO()
        
        # Configure console
        utils.set_console_position(1408, 59, 520, 245, on_top=True)
        if(gameclient_hwnd):
            utils.set_title(f"Botofus - {gameclient_hwnd}")
        warnings.simplefilter('ignore', category=UserWarning)
        """
dsdsd
        dsdsd
        """
        # Configure user input
        self.userio.add_suppress_window(utils.get_console())

        # Focus client to trigger window event
        utils.set_focus_console()
        self.userio._set_hotkey_state(suppress=True, hotkeys=True)


    def run(self):
        # Automtaically login if selected
        if (self.args["autologin"]):
            self.login()

        # Print console menu
        print(f"Console HWND: {utils.get_console()}")
        while True:
            self.userio.select_from_menu({
                "Log in": self.login,
                "Extract text region": lambda: text_search.extract_text_region_interactive(self.args["gameclient_hwnd"]),
                "Extract text region any window": lambda: text_search.extract_text_region_interactive_screen(),
                "Create text record": lambda: capture.create_text_record(self, self.args["gameclient_hwnd"]),
                "Create data field": lambda: capture.create_data_field(self, self.args["gameclient_hwnd"]),
                "Load TextRecord JSON file": lambda: print(text_record.load_text_records("data/text_records.json"))
            }, title="Client", default=5)

    def login(self):
        # Make sure its ready to input account details (First play button)
        pass



def _parse_args():
    parser = argparse.ArgumentParser(
        description='Client controlling a single Dofus instance.')
    parser.add_argument("-u", "--username", help="account username")
    parser.add_argument("-p", "--password", help="account password")
    parser.add_argument("-c", "--character", help="character name")
    parser.add_argument("-t", "--title", help="console title")
    parser.add_argument("-w", "--gameclient-hwnd", type=int,
                        help="hwnd for corresponding dofus client")
    parser.add_argument("-a", "--autologin", action="store_true",
                        help="whether to automatically log in on startup")
    return vars(parser.parse_args())


def main():
    # Parse command line arguments
    args = _parse_args()

    # Create and run client
    c = Client(args)
    c.run()


if __name__ == "__main__":
    main()
