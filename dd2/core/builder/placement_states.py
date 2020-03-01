import time

import dd2.io as io
from . import events
import dd2.core.kinematics as kinematics
import dd2.common.state_machine as state_machine
import dd2.utils as utils

# Initialization
class _InitTowerPlacement(state_machine.State):
    def execute(self, context):
        event = context.event
        client = context.client

        start_coords, start_rotation = event.start_orientation
        end_coords, end_rotation = event.end_orientation
    
        # Change character if nessecary
        required_hero_slot = client.get_hero_slot(event.defense)
        if client.get_active_hero_slot() != required_hero_slot:
            utils.utils.set_hero_slot(client, required_hero_slot)

        # Place defense
        du_current = client.du_current.read()
        du_target = du_current + event.defense.initial_cost

        def _inner_loop():
            utils.utils.do_until(
                callable_=lambda *_: io.keyboard.press_and_release(event.defense.defense_slot.get_hotkey()),
                test=client.interactive_mode.read,
            )

            kinematics.move_rotate(client, start_coords, start_rotation, relative=False)
            time.sleep(0.4)
            io.mouse.click()
            kinematics.move_rotate(client, end_coords, end_rotation, relative=False)
            time.sleep(0.4)
            io.mouse.click()

        utils.utils.do_until(
                callable_=_inner_loop,
                test=client.du_current.read,
                target_value=du_target,
                on_retry=lambda *_: (io.mouse.right_click(), time.sleep(0.2)),
                retry=5,
                timeout=20
            )
        return None


class _InitNodePlacement(state_machine.State):
    def execute(self, context):
        event = context.event
        client = context.client

        # Change character if nessecary
        required_hero_slot = client.get_hero_slot(event.defense)
        if client.get_active_hero_slot() != required_hero_slot:
            utils.utils.set_hero_slot(client, required_hero_slot)

        # Place defense
        du_current = client.du_current.read()
        initial_cost = event.defense.initial_cost 
        chain_cost = event.defense.extension_cost * (len(event.orientations_2d) - 2)
        du_target = du_current + initial_cost + chain_cost

        def _inner_loop():
            node_counter = client.node_counter.read()

            utils.utils.do_until(
                callable_=lambda *_: io.keyboard.press_and_release(event.defense.defense_slot.get_hotkey()),
                test=client.interactive_mode.read
            )

            for i, orientation_2d in enumerate(event.orientations_2d):
                coords, rotation = orientation_2d
                node_counter_target = (node_counter + i) % 7 + 1
                utils.utils.do_until(
                    callable_=lambda *_: (
                        kinematics.move_rotate(client, coords, rotation, relative=False),
                        time.sleep(0.4),
                        io.mouse.click(),
                    ),
                    test=client.node_counter.read,
                    target_value=node_counter_target,
                    on_retry=lambda *_: (
                        io.win.set_focus(client.hwnd),
                        io.win.set_mouse_capture(client.hwnd)
                    )
                )
            utils.utils.do_until(
                callable_=lambda *_: io.keyboard.press_and_release("e"),
                test=client.interactive_mode.read,
                target_value=False
            )
            
        utils.utils.do_until(
                callable_=_inner_loop,
                test=client.du_current.read,
                target_value=du_target,
                retry=5,
                timeout=20
            )
        return None


class _InitAuraPlacement(state_machine.State):
    def execute(self, context):
        event = context.event
        client = context.client

        coords, rotation = event.orientation_2d

        # Change character if nessecary
        required_hero_slot = client.get_hero_slot(event.defense)
        if client.get_active_hero_slot() != required_hero_slot:
            utils.utils.set_hero_slot(client, required_hero_slot)

        # Place defense
        du_current = client.du_current.read()
        du_target = du_current + event.defense.initial_cost

        def _inner_loop():
            utils.utils.do_until(
                callable_=lambda *_: io.keyboard.press_and_release(event.defense.defense_slot.get_hotkey()),
                test=client.interactive_mode.read
            )

            utils.utils.do_until(
                callable_=lambda *_: (
                    kinematics.move_rotate(client, coords, rotation, relative=False),
                    time.sleep(0.4),
                    io.mouse.click()
                ),
                test=client.interactive_mode.read,
                target_value=False
            )
            
        utils.utils.do_until(
            callable_=_inner_loop,
            test=client.du_current.read,
            target_value=du_target,
            retry=5,
            timeout=20
        )
        return None


class _SetupPlacement(state_machine.State):
    def execute(self, context):
        context.target_du = 100




# Placement
class _StartPlacement(state_machine.State):
    def execute(self, context):
        # Place first defense



        # Assert that defense is placed
        if failed:
            return StartPlacementFailed
            

class _ExtendPlacement(state_machine.State):
    def execute(self, context):
        return super().execute(context)


class _EndPlacement(state_machine.State):
    def execute(self, context):
        return super().execute(context)


# Error handling
class _StartPlacementFailed(state_machine.State):
    def execute(self, context):
        return super().execute(context)


class _ExtendPlacementFailed(state_machine.State):
    def execute(self, context):
        return super().execute(context)


class _EndPlacementFailed(state_machine.State):
    def execute(self, context):
        return super().execute(context)


# Selling
class _SellDefense(state_machine.State):
    def execute(self, context):
        print("Selling defense...")
        print("Retrying event placement")
        if event_type := type(context.event) == events.TowerPlacementEvent:
            return InitTowerPlacement
        elif event_type == events.NodePlacementEvent:
            return InitNodePlacement
        else:
            return InitAuraPlacement

InitTowerPlacement = _InitTowerPlacement()
InitNodePlacement = _InitNodePlacement()
InitAuraPlacement = _InitAuraPlacement()
StartPlacement = _StartPlacement()
StartPlacementFailed = _StartPlacementFailed()
ExtendPlacement = _ExtendPlacement()
ExtendPlacementFailed = _ExtendPlacementFailed()
EndPlacement = _EndPlacement()
EndPlacementFailed = _EndPlacementFailed()
SellDefense = _SellDefense()
