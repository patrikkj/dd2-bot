from queue import SimpleQueue

from .singleton import Singleton
from .keyboard_io import KeyboardIO
from .mouse_io import MouseIO
from .win_io import WinIO


class UserIO(metaclass=Singleton):
    # Event queue format:     
    # "queue_name" -> ({hotkey -> callback}, [events], is_active)

    def __init__(self):
        self.event_queues = {"default": [{}, [], True]}
        self.win_io = WinIO(self)
        self.mouse_io = MouseIO(self)
        self.keyboard_io = KeyboardIO(self)
        

    # Events
    def get_events(self, event_queue):
        return self.event_queues[event_queue][1] if event_queue in self.event_queues else []

    def has_events(self, event_queue):
        return bool(self.event_queues.get(event_queue, [None, None, False])[1])

    def call_next(self, event_queue, *args):
        return self.pop_event(event_queue)(*args) if self.has_events(event_queue) else None

    def pop_event(self, event_queue):
        return self.get_events(event_queue).pop(0) if self.has_events(event_queue) else None
    
    def is_active(self, event_queue):
        return self.event_queues[event_queue][2] if event_queue in self.event_queues else False

    def set_active(self, event_queue, active=True):
        if event_queue in self.event_queues:
            self.event_queues[event_queue][2] = active

    def clear_queue(self, event_queue):
        self.get_events(event_queue).clear()

# Alias
user_io = UserIO()
win_io = user_io.win_io
mouse_io = user_io.mouse_io
keyboard_io = user_io.keyboard_io
