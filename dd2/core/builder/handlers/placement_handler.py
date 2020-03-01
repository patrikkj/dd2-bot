import dd2.common as common

from .. import placement_states as states
from ..events import placement_event as events
from . import event_handler


class PlacementEventHandler(event_handler.EventHandler):
    def __init__(self):
        super().__init__()
        self.event_to_state = {
            events.TowerPlacementEvent: states.InitTowerPlacement,
            events.NodePlacementEvent: states.InitNodePlacement,
            events.AuraPlacementEvent: states.InitAuraPlacement
        }
        self.state_machine = common.state_machine.StateMachine(
            states.InitTowerPlacement,
            states.InitNodePlacement,
            states.InitAuraPlacement,
            states.StartPlacement,
            states.StartPlacementFailed,
            states.ExtendPlacement,
            states.ExtendPlacementFailed,
            states.EndPlacement,
            states.EndPlacementFailed,
            states.SellDefense
        )

    def consume(self, event, client):
        init_state = self.event_to_state.get(type(event), None)
        if init_state is None:
            raise NotImplementedError(f"Cannot consume event of type {type(event).__name__}")
        
        # Create an empty context unique to this event consumption
        context = self.state_machine.create_context()

        # Populate context
        context.event = event
        context.client = client

        # Run state machine within this context
        self.state_machine.run_from_state(init_state, context)
