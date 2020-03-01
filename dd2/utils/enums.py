from enum import Enum, auto, unique
import dd2.utils.decorators as decorators


@unique
@decorators.json_serializable
class Slot(Enum):
    HERO_1 = 'f1'
    HERO_2 = 'f2'
    HERO_3 = 'f3'
    HERO_4 = 'f4'

    SPELL_1 = '5'
    SPELL_2 = '6'
    SPELL_3 = '7'
    SPELL_4 = '8'

    DEFENSE_1 = '1'
    DEFENSE_2 = '2'
    DEFENSE_3 = '3'
    DEFENSE_4 = '4'

    def get_hotkey(self):
        return self.value

@unique
@decorators.json_serializable
class Hero(Enum):
    SQUIRE = auto()
    APPRENTICE = auto()
    MONK = auto()
    HUNTRESS = auto()
    ABYSS_LORD = auto()
    EV2 = auto()

@unique
@decorators.json_serializable
class DefenseType(Enum):
    TOWER = auto()
    NODE = auto()
    AURA = auto()

@unique
@decorators.json_serializable
class Defense(Enum):
    CANNONBALL_TOWER = (Hero.SQUIRE, Slot.DEFENSE_1, DefenseType.TOWER, 30, 0)
    SPIKE_BLOCKADE = (Hero.SQUIRE, Slot.DEFENSE_2, DefenseType.TOWER, 30, 0)
    BALLISTA = (Hero.SQUIRE, Slot.DEFENSE_3, DefenseType.TOWER, 60, 0)
    TRAINING_DUMMY = (Hero.SQUIRE, Slot.DEFENSE_4, DefenseType.TOWER, 20, 0)

    FLAMETHROWER_TOWER = (Hero.APPRENTICE, Slot.DEFENSE_1, DefenseType.TOWER, 40, 0)
    ARCANE_BARRIER = (Hero.APPRENTICE, Slot.DEFENSE_2, DefenseType.TOWER, 30, 0)
    FROSTBITE_TOWER = (Hero.APPRENTICE, Slot.DEFENSE_3, DefenseType.TOWER, 30, 0)
    EARTHSHATTER_TOWER = (Hero.APPRENTICE, Slot.DEFENSE_4, DefenseType.TOWER, 60, 0)

    FLAME_AURA = (Hero.MONK, Slot.DEFENSE_1, DefenseType.AURA, 30, 0)
    BOOST_AURA = (Hero.MONK, Slot.DEFENSE_2, DefenseType.AURA, 40, 0)
    SKY_GUARD_TOWER = (Hero.MONK, Slot.DEFENSE_3, DefenseType.TOWER, 50, 0)
    LIGHTNING_STRIKE_AURA = (Hero.MONK, Slot.DEFENSE_4, DefenseType.AURA, 20, 0)

    EXPLOSIVE_TRAP = (Hero.HUNTRESS, Slot.DEFENSE_1, DefenseType.AURA, 20, 0)
    GEYSER_TRAP = (Hero.HUNTRESS, Slot.DEFENSE_2, DefenseType.AURA, 30)
    POISON_DART_TOWER = (Hero.HUNTRESS, Slot.DEFENSE_3, DefenseType.TOWER, 40, 0)
    BLAZE_BALLOON = (Hero.HUNTRESS, Slot.DEFENSE_4, DefenseType.AURA, 60, 0)

    ORC_BLOCKADE = (Hero.ABYSS_LORD, Slot.DEFENSE_1, DefenseType.TOWER, 30, 0)
    SKELETAL_RAMSTER = (Hero.ABYSS_LORD, Slot.DEFENSE_2, DefenseType.TOWER, 50, 0)
    BONE_ARCHERS = (Hero.ABYSS_LORD, Slot.DEFENSE_3, DefenseType.TOWER, 40, 0)
    THE_COLOSSUS = (Hero.ABYSS_LORD, Slot.DEFENSE_4, DefenseType.AURA, 80, 0)

    PROTON_BEAM = (Hero.EV2, Slot.DEFENSE_1, DefenseType.NODE, 30, 10)
    REFLECT_BEAM = (Hero.EV2, Slot.DEFENSE_2, DefenseType.NODE, 30, 10)
    BUFF_BEAM = (Hero.EV2, Slot.DEFENSE_3, DefenseType.NODE, 60, 30)
    WEAPON_MANUFACTURER = (Hero.EV2, Slot.DEFENSE_4, DefenseType.NODE, 60, 30)

    @property
    def hero(self):
        return self.value[0]

    @property
    def defense_slot(self):
        return self.value[1]
        
    @property
    def defense_type(self):
        return self.value[2]

    @property
    def initial_cost(self):
        return self.value[3]

    @property
    def extension_cost(self):
        return self.value[4]

@unique
@decorators.json_serializable
class State(Enum):
    PRE_INIT_BUILD_PHASE = 8
    INIT_BUILD_PHASE = 0x802
    COMBAT_PHASE = 0x203
    PRE_BUILD_PHASE = 0x304
    BUILD_PHASE = 0x302
    PRE_POST_COMBAT_PHASE = 0x305
    POST_COMBAT_PHASE = 0x506
    SUMMARY_SCREEN = 0x607

    TOWN = 0x0
    PRIVATE_TAVERN = 0x1000000

    INVALID = -1

    @staticmethod
    def from_count(state_count):
        count_mapping = {
            1: State.PRE_INIT_BUILD_PHASE,
            2: State.INIT_BUILD_PHASE,
            3: State.COMBAT_PHASE,
            4: State.PRE_BUILD_PHASE,
            5: State.BUILD_PHASE,
            6: State.COMBAT_PHASE,
            7: State.PRE_BUILD_PHASE,
            8: State.BUILD_PHASE,
            9: State.COMBAT_PHASE,
            10: State.PRE_BUILD_PHASE,
            11: State.BUILD_PHASE,
            12: State.COMBAT_PHASE,
            13: State.PRE_BUILD_PHASE,
            14: State.BUILD_PHASE,
            15: State.COMBAT_PHASE,
            16: State.PRE_POST_COMBAT_PHASE,
            17: State.POST_COMBAT_PHASE,
            18: State.PRE_INIT_BUILD_PHASE,
        }
        return count_mapping.get(state_count, None) 
    
    @classmethod
    def _missing_(cls, _):
        print(f"ERROR: Fetched unknown state '{_}'")
        return State.INVALID


# Memory management
# Preprocessing
def invert_y(y):
    return -y

def normalize_yaw(yaw):
    return ((yaw - 0.5) % 2) - 1

def normalize_yaw_abs(yaw):
    return yaw - 1.5

def state_to_enum(state):
    return State(state)

def count_to_enum(count):
    return State.from_count(count)

def print_val(v):
    return (print(v), v)[1]

# invert_y = lambda y: -y
# normalize_yaw = lambda yaw: ((yaw - 0.5) % 2) - 1
# normalize_yaw_abs = lambda yaw: yaw - 1.5
# state_to_enum = State
# count_to_enum = State.from_count
# print_val = lambda v: (print(v), v)[1]

# Memory struct offsets
PLAYER_BASE_OFFSETS = (0x228, 0x358, 0x28C, 0x4F8, 0x134, 0x34, 0x015C5738)
VELOCITY_BASE_OFFSETS = (0xA4, 0x0, 0x015C5750)
HERO_DETAILS_OFFSETS = (0x28C, 0xC, 0x4E0, 0x4, 0x015E748C)
HERO_1_DETAILS_OFFSETS = (0x0, 0x950, 0x0, 0x015C56E0)
HERO_2_DETAILS_OFFSETS = (0xC, 0x950, 0x0, 0x015C56E0)
HERO_3_DETAILS_OFFSETS = (0x18, 0x950, 0x0, 0x015C56E0)
HERO_4_DETAILS_OFFSETS = (0x24, 0x950, 0x0, 0x015C56E0)
CAMERA_BASE_OFFSETS = (0x0, 0x184, 0x4F8, 0x134, 0x0, 0x015C5738)
MAPDATA_BASE_OFFSETS = (0x4B0, 0x134, 0x50, 0x015C5738)
# INPUT_BASE_OFFSETS = (0x0, 0x5A4, 0xB88, 0x3CC, 0x2C, 0x558, 0x430, 0x0156A098)
# INPUT_BASE_OFFSETS = (0x0, 0x5A4, 0x944, 0x10, 0x398, 0x3CC, 0x2C, 0x01568924)
INPUT_BASE_OFFSETS = (0x0, 0x5A4, 0x4F8, 0x134, 0x34, 0x015C5738)
# INPUT_BASE_OFFSETS = (0x0, 0x5A4, 0xB88, 0xACC, 0x0156B294)
# INPUT_BASE_OFFSETS = (0x0, 0x944, 0x10, 0x398, 0x56C, 0x55C, 0x015640E8)

class Variable(Enum):
    # VARIABLE   ->   ((Memory offsets), dtype, transform, inv_transform)
    PLAYER_X = (0xB0, PLAYER_BASE_OFFSETS, 'f', None, None)
    PLAYER_Y = (0xB4, PLAYER_BASE_OFFSETS, 'f', invert_y, None)
    PLAYER_Z = (0xB8, PLAYER_BASE_OFFSETS, 'f', None, None)

    VELOCITY_X = (0xB0, VELOCITY_BASE_OFFSETS, 'f', None, None)
    VELOCITY_Y = (0xB4, VELOCITY_BASE_OFFSETS, 'f', invert_y, None)
    VELOCITY_Z = (0xB8, VELOCITY_BASE_OFFSETS, 'f', None, None)

    PLAYER_DU = (0xE84, HERO_DETAILS_OFFSETS, 'i', None, None)
    PLAYER_1_DU = (0xE84, HERO_1_DETAILS_OFFSETS, 'i', None, None)
    PLAYER_2_DU = (0xE84, HERO_2_DETAILS_OFFSETS, 'i', None, None)
    PLAYER_3_DU = (0xE84, HERO_3_DETAILS_OFFSETS, 'i', None, None)
    PLAYER_4_DU = (0xE84, HERO_4_DETAILS_OFFSETS, 'i', None, None)
    PLAYER_DU_MAX = (0xE88, HERO_DETAILS_OFFSETS, 'i', None, None)
    PLAYER_MANA = (0xE7C, HERO_DETAILS_OFFSETS, 'i', None, None)
    PLAYER_MANA_MAX = (0xE80, HERO_DETAILS_OFFSETS, 'i', None, None)

    CAMERA_X = (0x58, CAMERA_BASE_OFFSETS, 'f', None, None)
    CAMERA_Y = (0x5C, CAMERA_BASE_OFFSETS, 'f', None, None)
    CAMERA_Z = (0x60, CAMERA_BASE_OFFSETS, 'f', None, None)
    PITCH = (0x638, CAMERA_BASE_OFFSETS, 'f', None, None)
    YAW = (0x600, CAMERA_BASE_OFFSETS, 'f', normalize_yaw, None)
    YAW_ABS = (0x600, CAMERA_BASE_OFFSETS, 'f', normalize_yaw_abs, None)
    FOV = (0x298, CAMERA_BASE_OFFSETS, 'f', None, None)
    ZOOM = (0x914, CAMERA_BASE_OFFSETS, 'f', None, None)

    SCORE = (0xAEC, MAPDATA_BASE_OFFSETS, 'i', None, None)
    MOBS_KILLED = (0x540, MAPDATA_BASE_OFFSETS, 'i', None, None)
    DU_CURRENT = (0x548, MAPDATA_BASE_OFFSETS, 'i', None, None)
    DU_MAX = (0x54C, MAPDATA_BASE_OFFSETS, 'i', None, None)
    PLAYER_COUNT = (0x448, MAPDATA_BASE_OFFSETS, 'i', None, None)
    READY_COUNT = (0xB10, MAPDATA_BASE_OFFSETS, 'i', None, None)
    IN_PARTY = (0xA40, MAPDATA_BASE_OFFSETS, 'i', None, None)
    TIME_ELAPSED = (0x294, MAPDATA_BASE_OFFSETS, 'i', None, None)
    UNSTABLE = (0x348, MAPDATA_BASE_OFFSETS, 'i', None, None)
    STATE = (0x3BC, MAPDATA_BASE_OFFSETS, 'i', state_to_enum, None)
    STATE_COUNTER = (0x708, MAPDATA_BASE_OFFSETS, 'i', count_to_enum, None)

    INPUT_X = (0x160, INPUT_BASE_OFFSETS, 'f', None, None)
    INPUT_Y = (0x15C, INPUT_BASE_OFFSETS, 'f', None, None)
    INPUT_Y_CONTROLLER = (0x120, INPUT_BASE_OFFSETS, 'f', None, None)
    INPUT_X_CONTROLLER = (0x138, INPUT_BASE_OFFSETS, 'f', None, None)

    MOB_COUNT_ALIVE = (0x7C, (0x6C0, 0x134, 0x0, 0x015C5738), 'i', None, None)
    INTERACTIVE_MODE = (0xBE4, (0x44, 0x78, 0x4, 0x015E748C), 'i', bool, None)
    NODE_COUNTER = (0x2FC, (0x34C, 0x74, 0x990, 0x0155938C), 'i', None, None)    
    
    @property
    def final_offset(self):
        return self.value[0]
        
    @property
    def block_offset(self):
        return self.value[1]
        
    @property
    def full_offset(self):
        return (self.final_offset, ) + self.block_offset
        
    @property
    def dtype(self):
        return self.value[2]
        
    @property
    def transform(self):
        return self.value[3]
        
    @property
    def inv_transform(self):
        return self.value[4]


class Folder(Enum):
    TEMPLATES_DIR = "dd2/resources/templates"
    MAPS_DIR = "dd2/resources/maps"
    IMAGES_DIR = "dd2/resources/images"
