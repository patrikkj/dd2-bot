import sys
import time

import numpy as np

import dd2.io as io
import dd2.models as models
import dd2.utils as utils

# Module level scope pointer
this = sys.modules[__name__]
this.pressed_set = set()
this.client_params = {}

MOVE_INJECT = True

ANGULAR_EPSILON = 0.01

MAX_ITER_DISTANCE = 200
LOOKAHEAD_DISTANCE = 20

DISTANCE_EPSILON_START = 10
DISTANCE_EPSILON_WALKING = 10
DISTANCE_EPSILON_JUMPING = 25
DISTANCE_EPSILON_END = 10
DISTANCE_EPSILON_BUILDING = 10


def _move_press_if_released(key):
    if key not in this.pressed_set:
        io.keyboard.press(key)
        this.pressed_set.add(key)

def _move_release_if_pressed(key):
    if key in this.pressed_set:
        io.keyboard.release(key)

def _move_input(theta, client=None):
    if theta > ANGULAR_EPSILON:
        _move_release_if_pressed('a')
        _move_press_if_released('d')
    elif theta < -ANGULAR_EPSILON:
        _move_release_if_pressed('d')
        _move_press_if_released('a')
    else:        
        _move_release_if_pressed('a')
        _move_release_if_pressed('d')

    if abs(theta) > (0.5 + ANGULAR_EPSILON):
        _move_release_if_pressed('w')
        _move_press_if_released('s')
    elif abs(theta) < (0.5 - ANGULAR_EPSILON):
        _move_release_if_pressed('s')
        _move_press_if_released('w')
    else:
        _move_release_if_pressed('w')
        _move_release_if_pressed('s')

def _move_input_inject(theta, client):
    if theta > ANGULAR_EPSILON:
        io.keyboard.set_input_x(client, 1)
    elif theta < -ANGULAR_EPSILON:
        io.keyboard.set_input_x(client, -1)
    else:        
        io.keyboard.set_input_x(client, 0)

    if abs(theta) > (0.5 + ANGULAR_EPSILON):
        io.keyboard.set_input_y(client, -1)
    elif abs(theta) < (0.5 - ANGULAR_EPSILON):
        io.keyboard.set_input_y(client, 1)
    else:
        io.keyboard.set_input_y(client, 0)


def _reset_key_state(client):
    io.keyboard.stash_state()
    io.keyboard.release('w')
    io.keyboard.release('a')
    io.keyboard.release('s')
    io.keyboard.release('d')
    this.pressed_set = set()

def _reset_key_state_inject(client):
    io.keyboard.set_input_vector(client, (0, 0))

# Override normal move input function
if MOVE_INJECT:
    _move_input = _move_input_inject
    _reset_key_state = _reset_key_state_inject


def traverse_path(client, path):
    _reset_key_state(client)

    # Player and line data
    end_coords = path.coords[-1][:2]
    player_coords = client.player_coords_2d.read()
    line_coord, _, line_theta, t = path.find_nearest_point(player_coords)
    
    # Loop until goal is reached
    while (distance := utils.math.euclidean_distance(player_coords, end_coords)) > DISTANCE_EPSILON_WALKING:
        # Create path target using projection and lookahead vector
        line_coord, _, line_theta, t = path.find_nearest_point_iterative(player_coords, t, MAX_ITER_DISTANCE=MAX_ITER_DISTANCE)
        lookahead = utils.math.to_normalized_vector(line_theta) * LOOKAHEAD_DISTANCE
        line_target = line_coord + lookahead
        if distance < 2 * LOOKAHEAD_DISTANCE:
            line_target = end_coords
        theta_to_target = utils.math.relative_angle(player_coords, client.yaw.read(), line_target) 

        # Execute movement
        _player_coords = player_coords
        _move_input(theta_to_target, client)
            
        # Wait for game loop to register keyboard input
        while np.array_equal(player_coords, _player_coords):
            player_coords = client.player_coords_2d.read()

    _reset_key_state(client)
    # print(f"Final distance: {distance}")

def move(client, target_coords, relative=False):
    _reset_key_state(client)
    # Player and line data
    player_coords = client.player_coords_2d.read()
    if relative:
        target_coords = np.add(target_coords, player_coords)
    line = models.line.Line(player_coords, target_coords)
    
    # Create static lookahead vector
    lookahead = line.unit_vector * LOOKAHEAD_DISTANCE

    # Loop until goal is reached
    while (distance := utils.math.euclidean_distance(player_coords, target_coords)) > DISTANCE_EPSILON_WALKING:
        # Create line target using projection and lookahead vector
        line_target = line.find_nearest_point(player_coords) + lookahead
        if distance < 4 * LOOKAHEAD_DISTANCE:
            line_target = target_coords
        theta_to_target = utils.math.relative_angle(player_coords, client.yaw.read(), line_target) 
        
        # Execute movement
        _player_coords = player_coords
        # print(player_coords, client.yaw.read(), line_target, theta_to_target, distance, sep='\t')
        _move_input(theta_to_target, client)
            
        # Wait for game loop to register keyboard input
        while np.array_equal(player_coords, _player_coords):
            player_coords = client.player_coords_2d.read()
        # player_coords = client.player_coords_2d.read()

    _reset_key_state(client)
    # print(f"Final distance: {distance}")

def jump(client, target_coords, relative=False):
    _reset_key_state(client)
    # Player and line data
    player_coords = client.player_coords_2d.read()
    if relative:
        target_coords = np.add(target_coords, player_coords)
    line = models.line.Line(player_coords, target_coords)
    
    # Create static lookahead vector
    # lookahead = 2 * line.unit_vector * LOOKAHEAD_DISTANCE
    prev_jump = 0
    # Loop until goal is reached
    while (distance := utils.math.euclidean_distance(player_coords, target_coords)) > DISTANCE_EPSILON_JUMPING:
        if (t := time.perf_counter() - prev_jump) > 4:
            io.keyboard.press_and_release("space")
            prev_jump = t
            
        # Create line target using projection and lookahead vector
        line_target = line.find_ease_in_out(t)
        # if distance < 4 * LOOKAHEAD_DISTANCE:
        #     line_target = target_coords
        theta_to_target = utils.math.relative_angle(player_coords, client.yaw.read(), line_target) 
        
        # Execute movement
        _player_coords = player_coords
        _move_input(theta_to_target, client)
            
        # Wait for game loop to register keyboard input
        while np.array_equal(player_coords, _player_coords):
            player_coords = client.player_coords_2d.read()

    _reset_key_state(client)
    # print(f"Final distance: {distance}")
