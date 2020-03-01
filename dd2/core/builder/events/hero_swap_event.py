import dd2.game as game
import dd2.utils as utils

from . import event

session = game.session.get()


@utils.decorators.json_serializable
class HeroSwapEvent(event.Event):
    def __init__(self, hero_slot):
        self.hero_slot = hero_slot

    @staticmethod
    def create():
        return HeroSwapEvent(utils.utils.get_hero_slot(session['client_active'].hwnd))
