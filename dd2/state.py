import cv2.cv2 as cv2
import time
from abc import ABC, abstractmethod
from dd2.utils import utils, templates
from dd2.io import file_io, keyboard_io, mouse_io, screen_io, win_io
from dd2.io.helpers import _file_io, _keyboard_io, _mouse_io, _screen_io, _win_io

# Alias
Field = utils.Field

class State(ABC):
    @abstractmethod
    def execute(self, session):
        pass

    def __str__(self):
        return self.__class__.__name__

    
class _LoadingScreen(State):
    def execute(self, session):
        for hwnd in session['client_hwnds']:
            win_io.set_focus(hwnd)
            
            # Loop until Prebuild phase is detected
            utils.compare_until_threshold(templates.DU_ZERO, hwnd)
            utils.compare_until_threshold(templates.WAVE_ONE_FIVE, hwnd)
            utils.compare_until_threshold(templates.MOBS_ZERO, hwnd)

        win_io.set_focus(session['client_main'][0])
        return PreBuildPhase

class _PreBuildPhase(State):
    def execute(self, session):

        # Handle all but last window
        for hwnd in session['client_hwnds'][:-1]:
            win_io.set_focus(hwnd)
            utils.compare_until_threshold(templates.MOBS_ZERO, session['client_active'][0])
            while not utils.compare_template(templates.CHARACTER_ACCEPT, hwnd):
                time.sleep(0.1)
                keyboard_io.press_and_release("g")
                time.sleep(0.1)
        
        # Handle last window
        last_hwnd = session['client_hwnds'][-1]
        win_io.set_focus(last_hwnd)
        utils.compare_until_threshold(templates.MOBS_ZERO, session['client_active'][0])
        while utils.compare_template(templates.MOBS_ZERO, last_hwnd):
                time.sleep(0.1)
                keyboard_io.press_and_release("g")
                time.sleep(0.1)

        win_io.set_focus(session['client_main'][0])
        return BuildPhase

class _BuildPhase(State):
    def execute(self, session):
        # Read wave data
        session['wave'] = utils.get_wave_count(session['client_active'][0])
        if session['wave'][0] == 1:
            # Wait until DU appears
            utils.compare_until_threshold(templates.DU_NONZERO, session['client_active'][0])

            # Drop DU
            du_status = [2] * (session['client_count']-1) 
            while sum(du_status) > 0: 
                for i, hwnd in enumerate(session['client_hwnds'][1:]):
                    print(f"DU Status: {du_status}")
                    win_io.set_focus(hwnd)
                    if utils.compare_template(templates.DU_ZERO, hwnd):
                        du_status[i] -= 1
                    else:
                        du_status = [2] * (session['client_count']-1) 
                        time.sleep(0.1)
                        keyboard_io.press_and_release("ctrl+m")
                        time.sleep(0.1)
            
            # Toggle back to main character
            win_io.set_focus(session['client_main'][0])
            utils.compare_until_threshold(templates.CHARACTER_ACCEPT, session['client_active'][0])

        # Handle all but last window
        for hwnd in session['client_hwnds'][:-1]:
            win_io.set_focus(hwnd)
            while not utils.compare_template(templates.CHARACTER_ACCEPT, hwnd):
                time.sleep(0.1)
                keyboard_io.press_and_release("g")
                time.sleep(0.1)
            
        # Handle last window
        last_hwnd = session['client_hwnds'][-1]
        win_io.set_focus(last_hwnd)
        utils.compare_until_threshold(templates.CHARACTER_NOACCEPT, session['client_active'][0])
        while utils.compare_template(templates.CHARACTER_NOACCEPT, last_hwnd):
                time.sleep(0.1)
                keyboard_io.press_and_release("g")
                time.sleep(0.1)

        win_io.set_focus(session['client_main'][0])
        return CombatPhase

class _CombatPhase(State):
    def execute(self, session):
        win_io.set_focus(session['client_main'][0])

        # Read wave data
        session['wave'] = utils.get_wave_count(session['client_active'][0])

        if session['wave'][0] in (1, 2, 3, 4):
            utils.read_field_until_value(Field.WAVE_COUNT, session['wave'][0] + 1, session['client_active'][0])
            return BuildPhase
        else:
            utils.read_field_until_value(Field.MOB_COUNT, 0, session['client_active'][0])
            return PostCombatPhase

class _PostCombatPhase(State):
    def execute(self, session):
        win_io.set_focus(session['client_main'][0])

        for hwnd in session['client_hwnds'][:-1]:
            win_io.set_focus(hwnd)
            while not utils.compare_template(templates.CHARACTER_ACCEPT, hwnd):
                time.sleep(0.1)
                keyboard_io.press_and_release("g")
                time.sleep(0.1)
            
        # Handle last window
        last_hwnd = session['client_hwnds'][-1]
        win_io.set_focus(last_hwnd)
        utils.compare_until_threshold(templates.CHARACTER_NOACCEPT, session['client_active'][0])
        while utils.compare_template(templates.CHARACTER_NOACCEPT, last_hwnd):
                time.sleep(0.1)
                keyboard_io.press_and_release("g")
                time.sleep(0.1)

        win_io.set_focus(session['client_main'][0])
        return SummaryScreen

class _SummaryScreen(State):
    def execute(self, session):
        win_io.set_focus(session['client_main'][0])
        utils.compare_until_threshold(templates.REPLAY, session['client_active'][0])

        # Click replay button
        while utils.compare_template(templates.MATCH_OVERVIEW, session['client_active'][0]):
                time.sleep(0.1)
                x, y = win_io.client_to_screen(session['client_active'][0], (826, 640))
                mouse_io.move_click(x, y, absolute=True, duration=1) 
                time.sleep(0.1)

        win_io.set_focus(session['client_main'][0])
        return LoadingScreen

class _Idle(State):
    def execute(self, session):
        return Idle

# External interface
LoadingScreen = _LoadingScreen()
PreBuildPhase = _PreBuildPhase()
BuildPhase = _BuildPhase()
CombatPhase = _CombatPhase()
PostCombatPhase = _PostCombatPhase()
SummaryScreen = _SummaryScreen()
Idle = _Idle()
