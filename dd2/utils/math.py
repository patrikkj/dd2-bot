import numpy as np

# Modes
# POINT_POINT
# ARRAY_POINT
# ARRAY_ARRAY


# Helpers
def _to_two_dims(coords):
    return coords[:, :2] if coords.ndim != 1 else coords[:2]

def _wrap_angle(angle):
    ''' Converts any angle to the range [-1, 1). '''
    return ((angle + 1) % 2) - 1

def get_angle(dx, dy):
    ''' # NOTE: This formula is modified to match the game coordinate system. '''
    return np.arctan2(dx, dy)/np.pi

def _align_shapes(coords_1, coords_2, row_per_axis=False):
    axis = int(not (row_per_axis or coords_1.ndim == coords_2.ndim == 1))
    if row_per_axis:
        coords_1 = np.vstack(coords_1) if coords_1.ndim == 1 else coords_1
        coords_2 = np.vstack(coords_2) if coords_2.ndim == 1 else coords_2
    return coords_1, coords_2, axis

def sum_of_squared_diffs(coords_1, coords_2, row_per_axis=False):
    coords_1, coords_2, axis = _align_shapes(coords_1, coords_2, row_per_axis)
    return np.sum(np.power(coords_1-coords_2, 2), axis=axis)

def euclidean_distance(coords_1, coords_2, row_per_axis=False):
    return np.sqrt(sum_of_squared_diffs(coords_1, coords_2, row_per_axis=row_per_axis))


# Conversion
def to_relative_coords(base_coords, coords):
    return coords - base_coords

def to_relative_angle(base_angle, angle):
    return _wrap_angle(angle - base_angle)

def to_absolute_coords(base_coords, coords):
    return base_coords + coords

def to_absolute_angle(base_angle, angle):
    return _wrap_angle(base_angle + angle)

def to_normalized_vector(angle):
    ''' # NOTE: This formula is modified to match the game coordinate system. '''
    rad = angle * np.pi
    return np.array((np.sin(rad), np.cos(rad)))

# Point - Point
def vector_between_points(p1, p2):
    return p2 - p1

def angle_between_points(p1, p2):
    return get_angle(*vector_between_points(p1, p2))


# Angle - Angle
def angular_difference(start_angle, end_angle, wrap=True):
    return _wrap_angle(end_angle - start_angle) if wrap else (end_angle - start_angle)
    # angles = end_angle - start_angle
    # if wrap:
    #     if angles.ndim == 1:
    #         angles[0] = _wrap_angle(angles[0]) 
    #     else:
    #         angles[:,0] = _wrap_angle(angles[:,0]) 
    # return angles

def angular_difference_pitch_yaw(start_angle, end_angle, wrap=True):
    angles = end_angle - start_angle
    if wrap:
        if angles.ndim == 1:
            angles[1] = _wrap_angle(angles[1]) 
        else:
            angles[:,1] = _wrap_angle(angles[:,1]) 
    return angles

# Relative 
def relative_angle(base_coords, base_yaw, target_coords):
    theta = angle_between_points(base_coords, target_coords)
    return angular_difference(base_yaw, theta)

def relative_vector(base_coords, base_yaw, target_coords):
    distance = euclidean_distance(base_coords, target_coords)
    theta = relative_angle(base_coords, base_yaw, target_coords)
    return to_normalized_vector(theta) * distance


# Functions
def ease_in_out(t, alpha=3):
    t = np.clip(t, 0, 1)
    return np.power(t, alpha) / (np.power(t, alpha) + np.power(1 - t, alpha))

def main():
    point_2d = np.array((123.456, 345.678))
    point_3d = np.array((123.456, 345.678, 567.890))

    points_2d = np.array([
        [9, 0, 2, 3],
        [1, 7, 5, 0]
    ])
    points_2d_t = points_2d.transpose()

    points_3d = np.array([
        [4, 4, 3, 1],
        [7, 1, 7, 9],
        [6, 8, 3, 3]
    ])
    points_3d_t = points_3d.transpose()

    arg1 = points_2d[:,1:]
    arg2 = points_2d[:,:-1]
    print(arg1, arg2)
    distances_from_start = np.insert(euclidean_distance(points_2d[:,1:], points_2d[:,:-1], row_per_axis=True), 0, 0).cumsum()
    print(f"Distance from start: {distances_from_start}")

    try:
        print("--- ROW PER AXIS ---")
        print("Point - Point")
        dist_pp = euclidean_distance(point_2d, point_2d*2)   
        print(dist_pp)
    except Exception as e:
        print(e)

    try:
        print("Array - Point")
        dist_ap = euclidean_distance(points_2d, point_2d*2, row_per_axis=True) 
        print(dist_ap)
    except Exception as e:
        print(e)

    try:
        print("Array - Array")
        dist_aa = euclidean_distance(points_2d, points_2d*2, row_per_axis=True) 
        print(dist_aa)
    except Exception as e:
        print(e)

    try:
        print("--- COORD PER ARRAY ---")
        print("Point - Point")
        dist_pp = euclidean_distance(point_2d, point_2d*2)
        print(dist_pp)
    except Exception as e:
        print(e)

    try:
        print("Array - Point")
        dist_ap = euclidean_distance(points_2d_t, point_2d*2)
        print(dist_ap)
    except Exception as e:
        print(e)

    try:
        print("Array - Array")
        dist_aa = euclidean_distance(points_2d_t, points_2d_t*2)
        print(dist_aa)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
