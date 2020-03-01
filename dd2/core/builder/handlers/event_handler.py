from abc import ABC, abstractmethod

class EventHandler(ABC):
    @abstractmethod
    def consume(self, event, client):
        pass

