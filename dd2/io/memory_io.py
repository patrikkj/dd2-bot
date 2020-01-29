from dd2.io.helpers import _file_io, _keyboard_io, _mouse_io, _screen_io, _win_io, _memory_io
from enum import Enum, auto

class Variable(Enum):
    PLAYER_X = auto()
    PLAYER_Y = auto()
    PLAYER_Z = auto()
    PLAYER_DU = auto()

    CAMERA_X = auto()
    CAMERA_Y = auto()
    CAMERA_Z = auto()
    PITCH = auto()
    YAW = auto()
    FOV = auto()
    ZOOM = auto()

    DU_CURRENT = auto()
    DU_MAX = auto()
    MOB_COUNT_ALIVE = auto()

# Preprocessing
normalize_yaw = lambda yaw: yaw % 2

variable_metadata = { 
    # VARIABLE   ->   ([Memory offsets], dtype, preprocessing)
    Variable.PLAYER_X: ([0xB0, 0x228, 0x358, 0x28C, 0xF8, 0x844, 0x0, 0x015C56E0], 'f', None),
    Variable.PLAYER_Y: ([0xB4, 0x228, 0x358, 0x28C, 0xF8, 0x844, 0x0, 0x015C56E0], 'f', None),
    Variable.PLAYER_Z: ([0xB8, 0x228, 0x358, 0x28C, 0xF8, 0x844, 0x0, 0x015C56E0], 'f', None),
    Variable.PLAYER_DU: ([0xE84, 0x0, 0x950, 0x0, 0x015C56E0], 'i', None),

    Variable.CAMERA_X: ([0x58, 0x0, 0x184, 0x4F8, 0x134, 0x0, 0x015C5738], 'f', None),
    Variable.CAMERA_Y: ([0x5C, 0x0, 0x184, 0x4F8, 0x134, 0x0, 0x015C5738], 'f', None),
    Variable.CAMERA_Z: ([0x60, 0x0, 0x184, 0x4F8, 0x134, 0x0, 0x015C5738], 'f', None),
    Variable.PITCH: ([0x638, 0x0, 0x184, 0x4F8, 0x134, 0x0, 0x015C5738], 'f', None),
    Variable.YAW: ([0x600, 0x0, 0x184, 0x4F8, 0x134, 0x0, 0x015C5738], 'f', normalize_yaw),
    Variable.FOV: ([0x298, 0x0, 0x184, 0x4F8, 0x134, 0x0, 0x015C5738], 'f', None),
    Variable.ZOOM: ([0x914, 0x0, 0x184, 0x4F8, 0x134, 0x0, 0x015C5738], 'f', None),

    Variable.DU_CURRENT: ([0x548, 0x0, 0x790, 0x0, 0x015C56E0], 'i', None),
    Variable.DU_MAX: ([0x54C, 0x0, 0x790, 0x0, 0x015C56E0], 'i', None),
    Variable.MOB_COUNT_ALIVE: ([0x7C, 0x6C0, 0x134, 0x0, 0x015C5738], 'i', None)
}


class MemoryData():
    def __init__(self, variable, process_handle, base_address):
        self.variable = variable
        self.process_handle = process_handle
        self.base_address = base_address
        self.pointer_address = None
        self.value = None
        self.offsets = variable_metadata[self.variable][0]
        self.dtype = variable_metadata[self.variable][1]
        self.preprocessing = variable_metadata[self.variable][2]
        
        self.update_pointer()
        self.fetch()
    
    def fetch(self):
        self.value = _memory_io.read_variable(self.process_handle, self.pointer_address, dtype=self.dtype)
        return self.preprocessing(self.value) if self.preprocessing else self.value

    def update_pointer(self):
        self.pointer_address = _memory_io.find_pointer_address(self.process_handle, self.base_address, self.offsets)

    def get_update(self):
        self.update_pointer()
        return self.fetch()


class MemoryDataGroup():
    def __init__(self, *pointers):
        self.pointers = pointers
    
    def fetch(self):
        return tuple(pointer.fetch() for pointer in self.pointers)

    def update_pointes(self):
        return tuple(pointer.update_pointes() for pointer in self.pointers)

    def get_update(self):
        return tuple(pointer.get_update() for pointer in self.pointers)

