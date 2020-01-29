from dd2.io import file_io, keyboard_io, mouse_io, screen_io, win_io, memory_io
from dd2.io.helpers import _file_io, _keyboard_io, _mouse_io, _screen_io, _win_io, _memory_io
from dd2.io.memory_io import Variable, MemoryData, MemoryDataGroup
# ---
from mouse import _winmouse as _os_mouse
# ---
import time
from matplotlib import pyplot


class Client():

    def __init__(self, hwnd, session):
        self.hwnd = hwnd
        self.session = session
        self.initialize()

    def initialize(self):
        # Fetch process data
        self.title = win_io.get_window_title(self.hwnd)
        self.pid, self.base_address = _memory_io.get_process_info(self.hwnd)

        # Create process handle with read access to process memory
        self.process_handle = _memory_io.create_process_handle(self.pid, _memory_io.PROCESS_ALL_ACCESS)

        # Create data fields
        self.x = MemoryData(Variable.PLAYER_X, self.process_handle, self.base_address)
        self.y = MemoryData(Variable.PLAYER_Y, self.process_handle, self.base_address)
        self.z = MemoryData(Variable.PLAYER_Z, self.process_handle, self.base_address)
        self.player_coords = MemoryDataGroup(self.x, self.y, self.z)

        self.cam_x = MemoryData(Variable.CAMERA_X, self.process_handle, self.base_address)
        self.cam_y = MemoryData(Variable.CAMERA_Y, self.process_handle, self.base_address)
        self.cam_z = MemoryData(Variable.CAMERA_Z, self.process_handle, self.base_address)
        self.cam_coords = MemoryDataGroup(self.cam_x, self.cam_y, self.cam_z)
        
        self.pitch = MemoryData(Variable.PITCH, self.process_handle, self.base_address)
        self.yaw = MemoryData(Variable.YAW, self.process_handle, self.base_address)
        self.fov = MemoryData(Variable.FOV, self.process_handle, self.base_address)
        self.zoom = MemoryData(Variable.ZOOM, self.process_handle, self.base_address)
        self.cam_rotation = MemoryDataGroup(self.pitch, self.yaw, self.fov, self.zoom)


        self.player_du = MemoryData(Variable.PLAYER_DU, self.process_handle, self.base_address)
        self.du_current = MemoryData(Variable.DU_CURRENT, self.process_handle, self.base_address)
        self.du_max = MemoryData(Variable.DU_MAX, self.process_handle, self.base_address)
        self.mob_count_alive = MemoryData(Variable.MOB_COUNT_ALIVE, self.process_handle, self.base_address)
        self.map_data = MemoryDataGroup(self.player_du, self.du_current, self.du_max, self.mob_count_alive)




    # Player movement

    def calibrate_camera(self, dx, dy, relative=True):
        mouse_map = {}
        # for delta in range(1,):
        for delta in range(50):
            delta = 1000
        # for delta in [1, 5, 10, 50, 100, 500, 1000, 2000]:
            _pitch, _yaw = self.pitch.get_update(), self.yaw.get_update()
            _os_mouse.move_relative(dx*delta, dy*delta)
            # time.sleep(0.2)
            while True:
                pitch, yaw = self.pitch.get_update(), self.yaw.get_update()
                if (pitch, yaw) != (_pitch, _yaw):
                    break
            
            d_pitch, d_yaw = pitch - _pitch, yaw - _yaw
            mouse_map[delta] = d_yaw
            # print(f"OLD   Pitch: {_pitch},   Yaw: {_yaw}")
            # print(f"NEW   Pitch: {pitch},   Yaw: {yaw}")
            # print(f"DIFF  Pitch: {d_pitch},   Yaw: {d_yaw}")
        # pyplot.plot(list(mouse_map.keys()), list(mouse_map.values()))
        # pyplot.xscale("log")
        # pyplot.show()

        for k, v in mouse_map.items():
            print(k, v)

    def debug(self):
        while True:
            print(self.player_coords.get_update(), self.cam_rotation.get_update())