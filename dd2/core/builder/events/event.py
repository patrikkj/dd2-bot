from abc import ABC

import dd2.utils.decorators as decorators


@decorators.json_serializable
class Event(ABC):
    def __str__(self):
        return self.__class__.__name__
