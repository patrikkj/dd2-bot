import dd2.io as io
from dd2.io.memory_io import MemoryData, MemoryDataBlock, MemoryDataGroup
from dd2.utils import utils
from dd2.utils.enums import Variable


class Client():
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.hero_slot_mapping = {}
        self.defense_mapping = {}
        self.active_hero_slot = None
        self.initialize()

    def initialize(self):
        # Fetch process data
        self.title = io.win.get_window_title(self.hwnd)
        self.pid, self.base_address = io._memory.get_process_info(self.hwnd)

        # Create process handle with read access to process memory
        self.process_handle = io._memory.create_process_handle(self.pid, io._memory.PROCESS_ALL_ACCESS)
        
        # Player details
        self.x = MemoryData(Variable.PLAYER_X, self.process_handle, self.base_address)
        self.y = MemoryData(Variable.PLAYER_Y, self.process_handle, self.base_address)
        self.z = MemoryData(Variable.PLAYER_Z, self.process_handle, self.base_address)
        self.player_coords_2d = MemoryDataGroup(self.x, self.y, numpify=True)
        self.player_coords = MemoryDataGroup(self.x, self.y, self.z, numpify=True)

        # Hero details
        self.player_du = MemoryData(Variable.PLAYER_DU, self.process_handle, self.base_address)
        self.player_1_du = MemoryData(Variable.PLAYER_1_DU, self.process_handle, self.base_address)
        self.player_2_du = MemoryData(Variable.PLAYER_2_DU, self.process_handle, self.base_address)
        self.player_3_du = MemoryData(Variable.PLAYER_3_DU, self.process_handle, self.base_address)
        self.player_4_du = MemoryData(Variable.PLAYER_4_DU, self.process_handle, self.base_address)
        self.player_du_all = MemoryDataGroup(self.player_1_du, self.player_2_du, self.player_3_du, self.player_4_du)

        self.player_du_max = MemoryData(Variable.PLAYER_DU_MAX, self.process_handle, self.base_address)
        self.player_mana = MemoryData(Variable.PLAYER_MANA, self.process_handle, self.base_address)
        self.player_mana_max = MemoryData(Variable.PLAYER_MANA_MAX, self.process_handle, self.base_address)

        # Camera
        self.cam_x = MemoryData(Variable.CAMERA_X, self.process_handle, self.base_address)
        self.cam_y = MemoryData(Variable.CAMERA_Y, self.process_handle, self.base_address)
        self.cam_z = MemoryData(Variable.CAMERA_Z, self.process_handle, self.base_address)
        self.cam_coords = MemoryDataGroup(self.cam_x, self.cam_y, self.cam_z, numpify=True)
        
        self.pitch = MemoryData(Variable.PITCH, self.process_handle, self.base_address)
        self.yaw = MemoryData(Variable.YAW, self.process_handle, self.base_address)
        self.yaw_abs = MemoryData(Variable.YAW_ABS, self.process_handle, self.base_address)
        self.rotation = MemoryDataGroup(self.pitch, self.yaw, numpify=True)
        self.rotation_abs = MemoryDataGroup(self.pitch, self.yaw_abs, numpify=True)
        
        self.fov = MemoryData(Variable.FOV, self.process_handle, self.base_address)
        self.zoom = MemoryData(Variable.ZOOM, self.process_handle, self.base_address)

        # Map data
        self.score = MemoryData(Variable.SCORE, self.process_handle, self.base_address)
        self.mobs_killed = MemoryData(Variable.MOBS_KILLED, self.process_handle, self.base_address)
        self.du_current = MemoryData(Variable.DU_CURRENT, self.process_handle, self.base_address)
        self.du_max = MemoryData(Variable.DU_MAX, self.process_handle, self.base_address)
        self.player_count = MemoryData(Variable.PLAYER_COUNT, self.process_handle, self.base_address)
        self.ready_count = MemoryData(Variable.READY_COUNT, self.process_handle, self.base_address)
        self.in_party = MemoryData(Variable.IN_PARTY, self.process_handle, self.base_address)
        self.time_elapsed = MemoryData(Variable.TIME_ELAPSED, self.process_handle, self.base_address)
        self.state = MemoryData(Variable.STATE, self.process_handle, self.base_address)
        self.state_counter = MemoryData(Variable.STATE_COUNTER, self.process_handle, self.base_address)

        self.mob_count_alive = MemoryData(Variable.MOB_COUNT_ALIVE, self.process_handle, self.base_address)
        self.interactive_mode = MemoryData(Variable.INTERACTIVE_MODE, self.process_handle, self.base_address)
        self.node_counter = MemoryData(Variable.NODE_COUNTER, self.process_handle, self.base_address)
        
        self.input_x = MemoryData(Variable.INPUT_X, self.process_handle, self.base_address)
        self.input_y = MemoryData(Variable.INPUT_Y, self.process_handle, self.base_address)
        self.input_x_controller = MemoryData(Variable.INPUT_X_CONTROLLER, self.process_handle, self.base_address)
        self.input_y_controller = MemoryData(Variable.INPUT_Y_CONTROLLER, self.process_handle, self.base_address)
        self.input_controllers = MemoryDataBlock(self.process_handle, self.base_address, 
            Variable.INPUT_X_CONTROLLER,
            Variable.INPUT_Y_CONTROLLER
        )

        # Compound fields
        self.orientation = MemoryDataGroup(self.player_coords, self.rotation)
        self.orientation_2d = MemoryDataGroup(self.player_coords_2d, self.rotation)


    def set_hero_slot_mapping(self, hero_slot_mapping):
        self.hero_slot_mapping = hero_slot_mapping
        self.defense_mapping = {}
        for hero_slot, defenses in self.hero_slot_mapping.items():
            for defense in defenses:
                self.defense_mapping[defense] = hero_slot

    def get_hero_slot(self, defense):
        return self.defense_mapping.get(defense, None)

    def get_defense(self, defense_slot, hero_slot=None):
        utils.update_hero_slot(self)
        _hero_slot = hero_slot if hero_slot else self.active_hero_slot
        defenses = self.hero_slot_mapping[_hero_slot]
        return next((d for d in defenses if d.defense_slot == defense_slot), None)

    def set_active_hero_slot(self, hero_slot):
        self.active_hero_slot = hero_slot
    
    def get_active_hero_slot(self):
        return self.active_hero_slot
