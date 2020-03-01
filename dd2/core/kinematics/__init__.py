from .camera_controller import rotate, rotate_pitch, rotate_yaw
from .movement_controller import move, jump, traverse_path

# Compound movements
def path_rotate(client, path, rotation):
    traverse_path(client, path)
    rotate(client, rotation)

def move_rotate(client, coords, rotation, relative=False):
    move(client, coords, relative)
    rotate(client, rotation)
