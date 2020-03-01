import sys
import time

import numpy as np
from mouse import _winmouse as _os_mouse

import dd2.game as game
import dd2.utils as utils

DEBUG = False
if DEBUG:
    import matplotlib.pyplot as plt
    plt.rcParams["figure.figsize"] = (9,7)
    plt.rcParams['lines.linewidth'] = 0.8
    plt.rcParams['lines.markersize'] = np.sqrt(10)
    plt.rcParams['legend.fontsize'] = 9

# Module level scope pointer
this = sys.modules[__name__]

this.client_params = {}
session = game.session.get()

GAIN_P = np.array((30, 80))
GAIN_I = np.array((0, 0))
GAIN_D = np.array((4, 8))
ANGULAR_THRESHOLD = 0.003
SLEEP_DURATION = 1/120


def rotate(client, target_rotation):
    # Instant rotation
    pitch, yaw = target_rotation
    client.pitch.write(pitch)
    client.yaw.write(yaw - 0.5)
    return 

    t_start = time.perf_counter()
    player_rotation = client.rotation_abs.read()
    initial_rotation = player_rotation
    output = np.zeros(2)

    if DEBUG:
        t_arr, p_arr, i_arr, d_arr = [], [], [], []

    # Deltas (Using relative yaw)
    delta_rotation = utils.math.angular_difference_pitch_yaw(client.rotation.read(), target_rotation)
    setpoint = initial_rotation + delta_rotation

    # PID Control system
    error_prev = 0
    t_prev = 0
    t = time.perf_counter() - t_start

    error, integral, derivative = delta_rotation, np.zeros(2), np.zeros(2)
    while abs(np.sqrt(error.dot(error))) > ANGULAR_THRESHOLD:
    # while t < 2:
        # Fetch new target
        t_prev, t = t, time.perf_counter() - t_start
        dt = t - t_prev
        
        player_rotation = client.rotation_abs.read()

        # Update parameters
        error_prev, error = error, utils.math.angular_difference_pitch_yaw(player_rotation, setpoint)
        integral += error*dt
        derivative = (error - error_prev)/dt

        # Evaluate
        p_corr, i_corr, d_corr = GAIN_P*error, GAIN_I*integral, GAIN_D*derivative
        correction = p_corr + i_corr + d_corr
        output += correction
        _player_rotation = player_rotation
        parsed_output = output.astype(int)[::-1]*np.array((1, -1))
        _os_mouse.move_relative(*parsed_output)

        # # Wait for game loop to register mouse input
        time.sleep(SLEEP_DURATION)
        while np.array_equal(player_rotation, _player_rotation) and output.astype(int).any():
            player_rotation = client.rotation_abs.read()

        if DEBUG:
            t_arr.append(t)
            p_arr.append(p_corr)
            i_arr.append(i_corr)
            d_arr.append(d_corr)
    
    if DEBUG:
        # Initialization
        fig = plt.figure()
        fig.suptitle('PID Controller analysis')
        fig.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.5,
                    wspace=0.35)
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)

        ax1.title.set_text('Pitch')
        ax1.set_xlabel('x')
        ax1.set_ylabel('gain')
        ax1.grid(True)

        ax2.title.set_text('Yaw')
        ax2.set_xlabel('t')
        ax2.set_ylabel('gain')
        ax2.grid(True)

        p_arr, i_arr, d_arr = np.array(p_arr), np.array(i_arr), np.array(d_arr)
        ax1.plot(t_arr, p_arr[:,0], t_arr, i_arr[:,0], t_arr, d_arr[:,0])
        ax2.plot(t_arr, p_arr[:,1], t_arr, i_arr[:,1], t_arr, d_arr[:,1])
        ax1.legend((f"P={GAIN_P[0]}", f"I={GAIN_I[0]}", f"D={GAIN_D[0]}"), loc=1)
        ax2.legend((f"P={GAIN_P[1]}", f"I={GAIN_I[1]}", f"D={GAIN_D[1]}"), loc=1)
        plt.show()

def rotate_yaw(client, target_yaw):
    t_start = time.perf_counter()
    initial_yaw = client.yaw_abs.read()
    player_yaw = initial_yaw
    output = 0

    # Deltas (Using relative yaw)
    delta_yaw = utils.math.angular_difference(client.yaw.read(), target_yaw)

    # PID Control system
    error_prev = 0
    t_prev = 0
    t = time.perf_counter() - t_start
    
    error, integral, derivative = delta_yaw, 0, 0
    while abs(error) > ANGULAR_THRESHOLD:
        # Fetch new target
        t_prev, t = t, time.perf_counter() - t_start
        dt = t - t_prev

        setpoint = initial_yaw + delta_yaw
        player_yaw = client.yaw_abs.read()

        # Update parameters
        error_prev, error = error, utils.math.angular_difference(player_yaw, setpoint)
        integral += error*dt
        derivative = (error - error_prev)/dt

        # Evaluate
        p_corr, i_corr, d_corr = GAIN_P[1]*error, GAIN_I[1]*integral, GAIN_D[1]*derivative
        correction = p_corr + i_corr + d_corr
        output += correction
        _player_yaw = player_yaw
        _os_mouse.move_relative(int(output), 0)

        # # Wait for game loop to register mouse input
        time.sleep(SLEEP_DURATION)
        while np.array_equal(player_yaw, _player_yaw) and int(output) != 0:
            player_yaw = client.yaw_abs.read()
    
    # print(f"[Yaw]: [{client.yaw.read():.8f}]")

def rotate_pitch(client, target_pitch):
    t_start = time.perf_counter()
    initial_pitch = client.pitch.read()
    player_pitch = initial_pitch
    output = 0

    # Deltas (Using relative pitch)
    delta_pitch = utils.math.angular_difference(initial_pitch, target_pitch, wrap=False)
    setpoint = initial_pitch + delta_pitch

    # PID Control system
    error_prev = 0
    t_prev = 0
    t = time.perf_counter() - t_start

    error, integral, derivative = delta_pitch, 0, 0
    while abs(error) > ANGULAR_THRESHOLD:
        # Fetch new target
        t_prev, t = t, time.perf_counter() - t_start
        dt = t - t_prev
        
        player_pitch = client.pitch.read()

        # Update parameters
        error_prev, error = error, utils.math.angular_difference(player_pitch, setpoint, wrap=False)
        integral += error*dt
        derivative = (error - error_prev)/dt

        # Evaluate
        p_corr, i_corr, d_corr = GAIN_P[0]*error, GAIN_I[0]*integral, GAIN_D[0]*derivative
        correction = p_corr + i_corr + d_corr
        output += correction
        _player_pitch = player_pitch
        _os_mouse.move_relative(0, -int(output))

        # # Wait for game loop to register mouse input
        time.sleep(SLEEP_DURATION)
        while np.array_equal(player_pitch, _player_pitch) and int(output) != 0:
            player_pitch = client.pitch.read()
    
    # print(f"[pitch]: [{client.pitch.read():.8f}]")
