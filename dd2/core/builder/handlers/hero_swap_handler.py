import time

import dd2.io as io
import dd2.utils as utils

from . import event_handler


class HeroSwapEventHandler(event_handler.EventHandler):
    def consume(self, event, client):
        while utils.utils.get_hero_slot(client.hwnd) != event.hero_slot:
            io.keyboard.press_and_release(event.hero_slot.value)
            time.sleep(0.2)
        return utils.utils.get_hero_slot(client.hwnd)
