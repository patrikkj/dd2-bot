import time
from abc import ABC, abstractmethod

import dd2.core.builder as builder
import dd2.io as io
import dd2.utils as utils
import dd2.utils.enums as enums

# Alias
Field = utils.utils.Field

class State(ABC):
    @abstractmethod
    def execute(self, session):
        pass
    
    @staticmethod
    def ready_into_state(session, state, on_retry=lambda *_: None):
        for target, client in enumerate(session['clients'][:-1], start=1):
            io.win.set_focus(client.hwnd)
            utils.utils.do_until(
                    callable_=lambda *_: io.keyboard.press_and_release("g"),
                    test=lambda *_: client.ready_count.read() >= target or client.state.read() == state,
                    on_retry=on_retry
            )
            if client.state.read() == state:
                io.win.set_focus(session['client_main'].hwnd)
                return

        
        last_client = session['clients'][-1]
        io.win.set_focus(last_client.hwnd)
        utils.utils.do_until(
                callable_=lambda *_: io.keyboard.press_and_release("g"),
                test=last_client.state.read,
                target_value=state,
                on_retry=on_retry
        )
        io.win.set_focus(session['client_main'].hwnd)

    
    @staticmethod
    def wait_until_state(session, *state, state_counter=False):
        client_main = session['client_main']
        func = client_main.state_counter if state_counter else client_main.state
        utils.utils.wait_until(lambda *_: func.read() in state)

    def __str__(self):
        return self.__class__.__name__

    
class _LoadingScreen(State):
    def execute(self, session):
        print("Before WaitUntilState in LoadingScreen")
        self.wait_until_state(session, enums.State.PRE_INIT_BUILD_PHASE)
        print("After WaitUntilState in LoadingScreen")
        return PreInitBuildPhase


class _PreInitBuildPhase(State):
    def execute(self, session):
        print("Before ReadyIntoState in PreInitBuildPhase")
        self.ready_into_state(session, enums.State.INIT_BUILD_PHASE)
        print("After ReadyIntoState in PreInitBuildPhase")
        time.sleep(5)
        return InitBuildPhase


class _InitBuildPhase(State):
    def execute(self, session):
        print("Start InitBuildPhase")
        # Wait until DU appears
        client_main = session['client_main']
        utils.utils.wait_until(lambda *_: client_main.player_du.read() != 0, timeout=10)
        time.sleep(1)

        # Drop DU to main client
        target_du = sum(client_main.player_du_all.read())
        def _inner_loop():
            mules = session['clients'][1:]
            while True:
                mules_du = {mule: mule.player_du.read() for mule in mules}
                for mule, player_du in mules_du.items():
                    if player_du:
                        utils.utils.do_until(
                            callable_=lambda *_: (
                                io.win.set_focus(mule.hwnd),
                                io.keyboard.press_and_release("ctrl+m")
                            ),
                            test=mule.player_du.read, 
                            target_value=0
                        )
                if not any(mules_du.values()):
                    break
        
        utils.utils.do_until(
            callable_=_inner_loop,
            test=client_main.player_du.read,
            target_value=target_du
        )
        io.win.set_focus(client_main.hwnd)

        # Toggle back to main character
        if session['auto_build']:
            builder.builder.build_sequence_by_name(session['auto_build_map_prefix'])
        else:
            utils.utils.wait_until(
                lambda *_: any([
                    client_main.ready_count.read() != 0, 
                    client_main.state.read() == enums.State.COMBAT_PHASE
                ])
            )
        self.ready_into_state(session, enums.State.COMBAT_PHASE)
        return CombatPhase


class _CombatPhase(State):
    def execute(self, session):
        client_main = session['client_main']
        self.wait_until_state(session, 
            enums.State.PRE_BUILD_PHASE, 
            enums.State.PRE_POST_COMBAT_PHASE, 
            enums.State.POST_COMBAT_PHASE
        )
        client_state = client_main.state.read()
        if client_state == enums.State.PRE_BUILD_PHASE:
            return PreBuildPhase
        if client_state == enums.State.PRE_POST_COMBAT_PHASE:
            return PrePostCombatPhase
        return PostCombatPhase


class _PreBuildPhase(State):
    def execute(self, session):
        self.wait_until_state(session, enums.State.BUILD_PHASE)
        return BuildPhase


class _BuildPhase(State):
    def execute(self, session):
        self.ready_into_state(session, enums.State.COMBAT_PHASE)
        return CombatPhase
        
    
class _PrePostCombatPhase(State):
    def execute(self, session):
        self.wait_until_state(session, enums.State.POST_COMBAT_PHASE)
        return PostCombatPhase


class _PostCombatPhase(State):
    def execute(self, session):
        self.ready_into_state(
            session, 
            enums.State.SUMMARY_SCREEN, 
            on_retry=lambda *_: io.keyboard.press_and_release("enter")
        )
        return SummaryScreen


class _SummaryScreen(State):
    def execute(self, session):
        # print("Before compare_until_threshold in _SummaryScreen")
        client_main = session['client_main']
        # utils.utils.compare_until_threshold(utils.templates.REPLAY, client_main.hwnd)
        # print("After compare_until_threshold in _SummaryScreen")

        def _enter_loop():
            io.keyboard.press_and_release("enter")
            time.sleep(1)

        utils.utils.do_until(
                callable_=_enter_loop,
                test=utils.utils.compare_template,
                test_args=(utils.templates.REPLAY, client_main.hwnd),
                target_value=True
        )

        def _inner_loop():
            x, y = io.win.client_to_screen(client_main.hwnd, (826, 640))
            io.mouse.move_click(x, y, absolute=True, duration=1) 

        utils.utils.do_until(
                callable_=_inner_loop,
                test=utils.utils.compare_template,
                test_args=(utils.templates.MATCH_OVERVIEW, client_main.hwnd),
                target_value=False
        )
        
        utils.utils.wait_until(lambda *_: client_main.state.read() != enums.State.SUMMARY_SCREEN)
        return LoadingScreen


class _Idle(State):
    def execute(self, session):
        return Idle
        

class _Pending(State):
    def __init__(self, name="Pending"):
        super().__init__()
        self.name = name

    def execute(self, session):
        print(f"Awaiting state change from {self.name}")
        _cached_state = session['client_main'].state.read()
        _state = _cached_state
        while not _state or _state == _cached_state:
            _state = session['client_main'].state.read()
            time.sleep(0.1)
        return state_map[_state]
        

# External interface
LoadingScreen = _LoadingScreen()
PreInitBuildPhase = _PreInitBuildPhase()
InitBuildPhase = _InitBuildPhase()
CombatPhase = _CombatPhase()
PreBuildPhase = _PreBuildPhase()
BuildPhase = _BuildPhase()
PrePostCombatPhase = _PrePostCombatPhase()
PostCombatPhase = _PostCombatPhase()
SummaryScreen = _SummaryScreen()
Idle = _Idle()
Pending = _Pending()
Town = _Pending("Town")
Tavern = _Pending("Tavern")

# Detect initial state
state_map = {
    enums.State.PRE_INIT_BUILD_PHASE: PreInitBuildPhase,
    enums.State.INIT_BUILD_PHASE: InitBuildPhase,
    enums.State.COMBAT_PHASE: CombatPhase,
    enums.State.PRE_BUILD_PHASE: PreBuildPhase,
    enums.State.BUILD_PHASE: BuildPhase,
    enums.State.POST_COMBAT_PHASE: PostCombatPhase,
    enums.State.SUMMARY_SCREEN: SummaryScreen,
    enums.State.TOWN: Town,
    enums.State.PRIVATE_TAVERN: Tavern
}

# States
def select_state(session):
    selected_state = io.keyboard.select_from_options({
        "Loading screen": LoadingScreen,
        "Pre-build phase": PreBuildPhase,
        "Build phase": BuildPhase,
        "Combat phase": CombatPhase,
        "Post-combat phase": PostCombatPhase,
        "Summary screen": SummaryScreen,
        "Idle": Idle,
    }, title="Select state")
    return session.set("state", selected_state)
