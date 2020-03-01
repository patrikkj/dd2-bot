from abc import ABC, abstractmethod


class StateMachine:
    def __init__(self, *states):
        self.states = states

    def create_context(self, state=None):
        """
        Creates an empty context. 
        If state is specified, this is passed as the initial state.
        """
        return Context(state)

    @staticmethod
    def run_from_state(state, context=None):
        '''
        Start the execution of the state machine from the state specified.
        If no context is given, creates an empty context.
        '''
        if context is None:
            context = Context()
        context.state = state
        context.start()

    @staticmethod
    def run(context):
        '''
        Start the execution of the state machine within the context specified.
        Runs until explicitly paused or a terminal state has been reached.
        '''
        context.started = True
        while context.state is not None:
            pass


class Context:
    """Container for allowing information to pass between states."""

    def __init__(self, state=None):
        self.state = state
        self.started = False
        self.paused = False
        self.terminated = False
        self.history = []

    def start(self):
        '''
        Start the execution of the state machine.
        Runs until explicitly paused or a terminal state has been reached.
        A state execution returning None is considered a terminal state transition.
        '''
        if self.state is None:
            raise AttributeError("Initial state is not specified.")

        self.started = True
        while self.state and not self.paused:
            self.state = self.state.execute(self)

    def resume(self):
        """Continue the execution of the state machine."""
        if self.terminated:
            raise ValueError("Cannot resume after reaching a terminal state.")

        self.paused = False
        self.start()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def started(self):
        return self._started

    @started.setter
    def started(self, started):
        self._started = started

    @property
    def paused(self):
        return self._paused

    @paused.setter
    def paused(self, paused):
        self._paused = paused

    @property
    def terminated(self):
        return self._terminated

    @terminated.setter
    def terminated(self, terminated):
        self._terminated = terminated


class State(ABC):
    @abstractmethod
    def execute(self, context):
        pass
