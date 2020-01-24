import cv2.cv2 as cv2
from abc import ABC, abstractmethod
from .utils import utils
from dd2.io.user_io import keyboard_io, mouse_io, user_io, win_io


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
            while (du_count := utils.get_DU(hwnd)[0]) != 0:
                print(du_count)
                cv2.waitKey(5) & 0xFF
            while (wave_count := utils.get_wave_count(hwnd)[0]) != 1:
                print(wave_count)
                cv2.waitKey(5) & 0xFF
            while (mob_count := utils.get_mob_count(hwnd)) != 0:
                print(mob_count)
                cv2.waitKey(5) & 0xFF

        return PreBuildPhase

class _PreBuildPhase(State):
    def execute(self, session):
        return BuildPhase

class _BuildPhase(State):
    def execute(self, session):
        return CombatPhase

class _CombatPhase(State):
    def execute(self, session):
        return PostCombatPhase

class _PostCombatPhase(State):
    def execute(self, session):
        return SummaryScreen

class _SummaryScreen(State):
    def execute(self, session):
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
