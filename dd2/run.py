from enum import Enum, auto
from userio import mouse_io as _mouse, keyboard_io as _keyboard, win_io as _win

class GameState(Enum):
    LOADING_SCREEN = auto()
    PRE_BUILD_PHASE = auto()
    BUILD_PHASE = auto()
    COMBAT_PHASE = auto()
    POST_COMBAT_PHASE = auto()
    SUMMARY_SCREEN = auto()
    IDLE = auto()

class GameLoop():
    def __init__(self):
        self.state = GameState.IDLE

    def run():
        while self.state != GameState.IDLE:




def main():
    game_loop = GameLoop()
    game_loop.run()


