import os
import re
from datetime import datetime
from enum import Enum

import cv2.cv2 as cv2


class Folder(Enum):
    TEMPLATES_DIR = os.path.abspath("dd2/resources/templates")
    IMAGES_DIR = os.path.abspath("dd2/resources/templates")

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
        prefix = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        filename = f"{prefix}.png"
    return cv2.imwrite(f"{Folder.IMAGES_DIR}/{filename}", image)

def save_template(image, x, y, dx, dy):
    prefix = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    suffix = f"[{x},{y},{dx},{dy}]"
    filename = f"{prefix}__{suffix}.png"
    return cv2.imwrite(f"{Folder.TEMPLATES_DIR}/{filename}", image)

def load_from_images(prefix, exact=False):
    if exact:
        filename = next(name for name in os.listdir(Folder.IMAGES_DIR) if name.equals(prefix))
    else:
        filename = next(name for name in os.listdir(Folder.IMAGES_DIR) if name.startswith(prefix))
    return cv2.imread(f"{Folder.IMAGES_DIR}/{filename}")

def load_from_templates(prefix, exact=False):
    if exact:
        filename = next(name for name in os.listdir(Folder.TEMPLATES_DIR) if name.equals(prefix))
    else:
        filename = next(name for name in os.listdir(Folder.TEMPLATES_DIR) if name.startswith(prefix))
    match = re.search(r'\[(\d+),(\d+),(\d+),(\d+)\]', filename)
    x, y, dx, dy = (int(e) for e in match.groups())
    return cv2.imread(f"{Folder.TEMPLATES_DIR}/{filename}"), (x, y, dx, dy)
