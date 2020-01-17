import os
import warnings

import keyboard

import botofus.loader as loader
import botofus.utils.utils as utils
import botofus.session as sess
import botofus.api.botofus_api as botofus_api
# from botofus.session import Session


# launcher_hwnd = None
# clients = {}        # HWND mapping from Botofus client CMD to game client


def launch():
    _setup()
    # session = _create_session()

    # Create event listener loopS
    print("Running Botofus API")
    botofus_api.run()

    # _run_launcher(session)
    # _run_client(session)
    # _run_console(session)
    # _kill()

    # utils.nested_print(session, indent=4)
    # utils.nested_print(session, indent=4)
    # utils.nested_print(session, indent=4)


def _create_session():
    session = sess.get()
    loader.load_config(session)
    loader.load_accounts(session)
    return session


def _setup():
    # Ignore user warnings
    warnings.simplefilter("ignore", category=UserWarning)


def _run_launcher(session):
    print("\n\n--- Launcher ---")

    # Assert that launcher is running
    launcher_identifier = session["config"]["launcher_identifier"]
    launcher_window = utils.get_window(launcher_identifier)
    if launcher_window is None:
        print("No launcher detected, running launcher.")
        path_to_launcher = session["config"]["path_to_launcher"]
        os.system(f"start {path_to_launcher}")

    # Wait for launcher to pop up
    print("Fetching launcher HWND.")
    launcher_hwnd, launcher_title = utils.ensure_window_exists(
        launcher_identifier)
    print("Launcher detected.")

    # Write launcher data to session
    session["launcher"] = (launcher_hwnd, launcher_title)
    session["launcher_hwnd"] = launcher_hwnd
    session["launcher_title"] = launcher_title


def _run_client(session):
    print("\n\n--- Clients ---")

    # Detect running clients
    gameclient_identifier = session["config"]["gameclient_identifier"]
    running_clients = utils.get_windows(gameclient_identifier)
    running_client_count = len(running_clients)

    # Autorun configuration
    auto_run = session["config"]["auto_run"]
    if auto_run:
        run_count = session["config"]["number_of_clients"] - \
            running_client_count

    # Ask user to input requested number of clients
    if running_clients and not auto_run:
        print(
            f"Detected {running_client_count} running game client{'' if running_client_count == 1 else 's'}.")
        for hwnd, title in running_clients:
            print(f"    Title: {title:30} Reference: {hwnd}")
        print()

        while True:
            utils.set_focus_console()
            run_count = input(
                "How many additional clients would you like to run (Blank = 0)?\n>>> ")
            if not run_count:
                run_count = 0
                break
            elif run_count.isdigit():
                run_count = int(run_count)
                break
            else:
                print("Something went wrong, input must be numeric or blank.")
    elif not auto_run:
        print(f"No running game clients detected.")
        while True:
            utils.set_focus_console()
            run_count = input(
                "How many clients would you like to run (Blank = 0)?\n>>> ")
            if not run_count:
                run_count = 0
                break
            elif run_count.isdigit():
                run_count = int(run_count)
                break
            else:
                print("Something went wrong, input must be numeric or blank.")

    # Wait for clients to load
    if run_count != 0:
        # Run clients
        print(f"Launcher HWND: {session['launcher_hwnd']}")
        utils.set_focus(session['launcher_hwnd'])
        utils.press_and_release(f"ctrl+{run_count}")
        print("Waiting for clients to load.")
        utils.ensure_window_exists_count(
            gameclient_identifier, len(running_clients) + run_count)
        utils.set_focus_console()
        print("Clients loaded.")

    # Write gameclient data to session
    session["gameclients"] = utils.get_windows(gameclient_identifier)
    session["gameclients_hwnd"] = [hwnd for hwnd, _ in session["gameclients"]]
    session["gameclients_count"] = len(session["gameclients"])
    

def _run_console(session):
    gameclient_identifier = session["config"]["gameclient_identifier"]
    windows = utils.get_windows(gameclient_identifier)
    for gameclient_hwnd, _ in windows:
        # Run console
        print(os.getcwd())
        os.system(
            f"start cmd /k python botofus/client.py --gameclient-hwnd {gameclient_hwnd} --autologin")
    # os.system("start cmd /k python client.py")
    

def _kill():
    exit()
