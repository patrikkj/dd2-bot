import os
import re
import numpy as np
from datetime import datetime
from enum import Enum

from dd2.io.helpers import _file_io, _keyboard_io, _mouse_io, _screen_io, _win_io
import cv2.cv2 as cv2


class Folder(Enum):
    TEMPLATES_DIR = "dd2/resources/templates"
    IMAGES_DIR = "dd2/resources/images"

# Directory handling
def names_from_directory(directory):
    return os.listdir(directory)

def paths_from_directory(directory):
    return [f"{directory}\\{image}" for image in os.listdir(directory)]

def images_from_directory(directory):
    return [cv2.imread(f"{directory}\\{image}") for image in os.listdir(directory)]


# Image IO
def save_image(image, filename=None):
    if not filename:
        prefix = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"{prefix}.png"
    path = os.path.join(os.path.abspath(Folder.IMAGES_DIR.value), filename)
    # image.save(path)
    cv2.imwrite(path, image)
    print(f"Saved image to: {path}")

def save_template(image, x, y, dx, dy):
    prefix = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    suffix = f"[{x},{y},{dx},{dy}]"
    filename = f"{prefix}__{suffix}.png"
    path = os.path.join(os.path.abspath(Folder.TEMPLATES_DIR.value), filename)
    # image.save(path)
    cv2.imwrite(path, image)
    print(f"Saved template to: {path}")

def load_from_images(prefix, exact=False):
    if exact:
        filename = next(name for name in os.listdir(Folder.IMAGES_DIR.value) if name.equals(prefix))
    else:
        filename = next(name for name in os.listdir(Folder.IMAGES_DIR.value) if name.startswith(prefix))
    path = os.path.join(os.path.abspath(Folder.IMAGES_DIR.value), filename)
    return cv2.imread(path)

def load_from_templates(prefix, exact=False):
    if exact:
        filename = next(name for name in os.listdir(Folder.TEMPLATES_DIR.value) if name.equals(prefix))
    else:
        filename = next(name for name in os.listdir(Folder.TEMPLATES_DIR.value) if name.startswith(prefix))
    match = re.search(r'\[(\d+),(\d+),(\d+),(\d+)\]', filename)
    x, y, dx, dy = (int(e) for e in match.groups())
    path = os.path.join(os.path.abspath(Folder.TEMPLATES_DIR.value), filename)
    return cv2.imread(path), (x, y, dx, dy)
