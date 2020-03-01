
import math
import numpy as np
import time
from mouse import _winmouse as _os_mouse
import dd2.io as io

from dd2.kinematics import utils.math

# Absolute coordinates
# --------------------
#
# y ^
#   |
#   |
#   |
#   o-------> x
#
# Angles are relative to Y axis. 
# Angle of -0.5     corresponds to -0.5 * π radians (= -90 degrees),    movement along neg. x axis
# Angle of 0        corresponds to 0 radians        (= 0 degrees),      movement along y axis
# Angle of 0.5      corresponds to 0.5 * π radians  (= 90 degrees),     movement along x axis
# Angle of 1        corresponds to π radians        (= 180 degrees),    movement along neg. y axis
# Absolute angle domain [-1, 1)


# Relative coordinates (used by '_relative_angle' and '_relative_vector')
# --------------------
#
# \   y ^     /
#  \    |    /
#   \   |   /
#    \  |  /
#     \ | /
#      \o/-----> x
#
# Angle of -0.5     corresponds to -0.5 * π radians (= -90 degrees),    movement along neg. x axis
# Angle of 0        corresponds to 0 radians        (= 0 degrees),      movement along y axis
# Angle of 0.5      corresponds to 0.5 * π radians  (= 90 degrees),     movement along x axis
# Angle of 1        corresponds to π radians        (= 180 degrees),    movement along neg. y axis
# Relative angle domain [-1, 1)
DISTANCE_THRESHOLD = 15
ANGULAR_EPSILON = 0.01


def _euclidean_distance(p1, p2, three_dim=False):
    if not three_dim:
        return (sum((u - v)**2 for u, v in zip(p1[:2], p2[:2])))**0.5
    return (sum((u - v)**2 for u, v in zip(p1, p2)))**0.5

def _vector_between_points(p1, p2):
    return (p2[0]-p1[0], p2[1]-p1[1])
    
def _angle_between_points(p1, p2):
    dx = (p2[0]-p1[0])
    dy = (p2[1]-p1[1])
    return math.atan2(dx, dy)/math.pi

def _angular_difference_pitch(start_angle, end_angle):
    return end_angle - start_angle

def _angular_difference_yaw(start_angle, end_angle):
    diff = end_angle - start_angle
    if diff >= 1:
        return diff - 2
    if diff < -1:
        return diff + 2
    return diff

def _relative_angle(client, coords):
    theta = _angle_between_points(client.player_coords.read(), coords)
    return _angular_difference_yaw(client.yaw.read(), theta)

def _relative_vector(client, coords):
    distance = _euclidean_distance(client.player_coords.read(), coords)
    radians = _relative_angle(client, coords) * math.pi
    return (distance * math.sin(radians), distance * math.cos(radians))


# Camera management
def set_yaw(client, target_yaw):
    step_y = 128
    dy = _angular_difference_yaw(client.yaw.read(), target_yaw)
    _dy = dy

    # Loop until axis is downscaled
    while step_y:
        while dy * _dy > 0:
            sign_y = 1 if dy > 0 else -1
            _yaw = client.yaw.read()
            _os_mouse.move_relative(sign_y*step_y, 0)

            # Wait for game loop to register mouse input
            while client.yaw.read() == _yaw:
                pass

            _dy, dy = dy, _angular_difference_yaw(client.yaw.read(), target_yaw)
        _dy = dy
        step_y >>= 1
    # print(f"[Yaw, Delta]: [{client.yaw.read():.5f}, {dy:.5f}]")


def set_pitch(client, target_pitch):
    step_p = 128
    dp = _angular_difference_pitch(client.pitch.read(), target_pitch)
    _dp = dp

    # Loop until axis is downscaled
    while step_p:
        while dp * _dp > 0:
            sign_p = -1 if dp > 0 else 1
            _pitch = client.pitch.read()
            _os_mouse.move_relative(0, sign_p*step_p)

            # Wait for game loop to register mouse input
            while client.pitch.read() == _pitch:
                pass

            _dp, dp = dp, _angular_difference_pitch(client.pitch.read(), target_pitch)
        _dp = dp
        step_p >>= 1
    # print(f"[Pitch, Delta]: [{client.pitch.read():.5f}, {dp:.5f}]")

def rotate(client, rotation):
    rotation = tuple(rotation)
    target_pitch, target_yaw = rotation
    step_p, step_y = 128, 128

    # Initial diffs
    dp = _angular_difference_pitch(client.pitch.read(), target_pitch)
    dy = _angular_difference_yaw(client.yaw.read(), target_yaw)
    _dp, _dy = dp, dy

    # Loop until both axes are downscaled
    while step_p or step_y:
        while dp * _dp > 0 and dy * _dy > 0:
            sign_p = -1 if dp > 0 else 1
            sign_y = 1 if dy > 0 else -1
            _pitch = client.pitch.read()
            _yaw = client.yaw.read()
            _os_mouse.move_relative(sign_y*step_y, sign_p*step_p)

            # Wait for game loop to register mouse input
            while step_p and client.pitch.read() == _pitch:
                pass
            while step_y and client.yaw.read() == _yaw:
                pass

            _dp, dp = dp, _angular_difference_pitch(client.pitch.read(), target_pitch)
            _dy, dy = dy, _angular_difference_yaw(client.yaw.read(), target_yaw)
        
        if dp * _dp < 0:
            _dp = dp
            step_p >>= 1

        if dy * _dy < 0:
            _dy = dy
            step_y >>= 1
        
        _dp = dp
        _dy = dy
    dp = _angular_difference_pitch(client.pitch.read(), target_pitch)
    dy = _angular_difference_yaw(client.yaw.read(), target_yaw)
    dist = _euclidean_distance((0, 0), (dp, dy))
    # print(f"[Pitch, Yaw, Delta]: [{client.pitch.read():.5f}, {client.yaw.read():.5f}, {dist:.5f}]")


# Player management
def move(client, coords, relative=False, rotate_first=True):
    player_coords = client.player_coords_2d.read()
    _player_coords = player_coords
    if relative:
        target_coords = np.add(target_coords, player_coords)
    # distance = utils.math.euclidean_distance(player_coords, target_coords)
    if rotate_first:
        set_yaw(client, utils.math.angle_between_points(player_coords, target_coords))
    
    pressed_set = set()
    while (distance := utils.math.euclidean_distance(player_coords, target_coords)) > DISTANCE_THRESHOLD:
        theta = utils.math.relative_angle(player_coords, client.yaw.read(), target_coords)
        _player_coords = player_coords
        if theta > ANGULAR_EPSILON:
            if 'a' in pressed_set:
                io.keyboard.release('a')
                pressed_set.remove('a')
            if 'd' not in pressed_set:
                io.keyboard.press('d')
                pressed_set.add('d')
        elif theta < -ANGULAR_EPSILON:
            if 'd' in pressed_set:
                io.keyboard.release('d') 
                pressed_set.remove('d')
            if 'a' not in pressed_set:
                io.keyboard.press('a') 
                pressed_set.add('a')
        else:
            if 'a' in pressed_set:
                io.keyboard.release('a')
                pressed_set.remove('a')
            if 'd' in pressed_set:
                io.keyboard.release('d') 
                pressed_set.remove('d')

        if abs(theta) > (0.5 + ANGULAR_EPSILON):
            if 'w' in pressed_set:
                io.keyboard.release('w')
                pressed_set.remove('w')
            if 's' not in pressed_set:
                io.keyboard.press('s')
                pressed_set.add('s')
        elif abs(theta) < (0.5 - ANGULAR_EPSILON):
            if 's' in pressed_set:
                io.keyboard.release('s')
                pressed_set.remove('s')
            if 'w' not in pressed_set:
                io.keyboard.press('w')
                pressed_set.add('w')
        else:
            if 'w' in pressed_set:
                io.keyboard.release('w')
                pressed_set.remove('w')
            if 's' in pressed_set:
                io.keyboard.release('s') 
                pressed_set.remove('s')
        
        # Wait for game loop to register keyboard input
        while np.array_equal(player_coords, _player_coords):
            player_coords = client.player_coords_2d.read()
        # distance = _euclidean_distance(client.player_coords.read(), target_coords)

    io.keyboard.release('w')
    io.keyboard.release('a')
    io.keyboard.release('s')
    io.keyboard.release('d')
    print(f"Final distance: {distance}")

def move_rotate(client, coords, rotation, relative=False, rotate_first=True):
    move(client, coords, relative=relative, rotate_first=rotate_first)
    rotate(client, rotation)
