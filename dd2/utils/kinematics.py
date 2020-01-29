
import math
from mouse import _winmouse as _os_mouse


def _euclidean_distance(p1, p2):
    return (sum((u - v)**2 for u, v in zip(p1, p2)))**0.5

def _vector_between_points(p1, p2):
    return (p2[0]-p1[0], p2[1]-p1[1])
    
def _angle_between_points(p1, p2):
    dx = (p2[0]-p1[0])
    dy = (p2[1]-p1[1])
    return math.atan(dy/dx)/math.pi

def _angular_difference(theta1, theta2):
    diff = theta1 - theta2
    return diff if abs(diff) < 1 else diff - 2


def rotate_camera(client, target_yaw):
    diff = client.yaw.get_update() - target_yaw
    _diff = diff
    for delta in [128, 64, 32, 16, 8, 4, 2, 1]:    
        while diff*_diff > 0:
            sign_y = -1 if diff > 0 else 1
            _yaw = client.yaw.get_update()
            _os_mouse.move_relative(sign_y*delta, 0)
            while client.yaw.get_update() == _yaw:
                pass
            _diff = diff
            diff = client.yaw.get_update() - target_yaw
            # print(delta, client.yaw.get_update())
        _diff = diff
    print(f"Deviation: {client.yaw.get_update() - target_yaw}")

def tilt_camera(client, target_pitch):
    diff = client.pitch.get_update() - target_pitch
    _diff = diff
    for delta in [128, 64, 32, 16, 8, 4, 2, 1]:    
        while diff*_diff > 0:
            sign_p = -1 if diff < 0 else 1
            _pitch = client.pitch.get_update()
            _os_mouse.move_relative(0, sign_p*delta)
            while client.pitch.get_update() == _pitch:
                pass
            _diff = diff
            diff = client.pitch.get_update() - target_pitch
            # print(delta, client.pitch.get_update())
        _diff = diff
    print(f"Deviation: {client.pitch.get_update() - target_pitch}")


def rotate(client, target_pitch=None, target_yaw=None):
    scalar_p, scalar_y = 128, 128

    if target_pitch is None:
        scalar_p = 0
    if target_yaw is None:
        scalar_y = 0

    # Initial diffs
    dp = _angular_difference(client.pitch.get_update(), target_pitch)
    dy = _angular_difference(client.yaw.get_update(), target_yaw)
    _dp, _dy = dp, dy

    # Loop until both axes are downscaled
    while scalar_p != 0 or scalar_y != 0:
        dpp = dp * _dp
        dyp = dy * _dy

        while dpp > 0 and dyp > 0:
            sign_p = -1 if dp < 0 else 1
            sign_y = -1 if dy > 0 else 1
            _pitch = client.pitch.get_update()
            _yaw = client.yaw.get_update()
            _os_mouse.move_relative(sign_y*scalar_y, sign_p*scalar_p)

            # Wait for game loop to register mouse input
            while scalar_p != 0 and client.pitch.get_update() == _pitch:
                pass
            while scalar_y != 0 and client.yaw.get_update() == _yaw:
                pass

            _dp = dp
            _dy = dy
            dp = _angular_difference(client.pitch.get_update(), target_pitch)
            dy = _angular_difference(client.yaw.get_update(), target_yaw)
            dpp = dp * _dp
            dyp = dy * _dy
        
        if dpp < 0:
            _dp = dp
            if scalar_p == 1:
                scalar_p = 0
            else:
                scalar_p /= 2

        if dyp < 0:
            _dy = dy
            if scalar_y == 1:
                scalar_y = 0
            else:
                scalar_y /= 2
        
        _dp = dp
        _dy = dy
    dp = _angular_difference(client.pitch.get_update(), target_pitch)
    dy = _angular_difference(client.yaw.get_update(), target_yaw)
    dist = _euclidean_distance((0, 0), (dp, dy))
    print(f"Deviation [Pitch, Yaw, Distance]\n[{dp:.7f}, {dy:.7f}, {dist:.7f}]")
