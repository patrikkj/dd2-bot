import json
import os
import re
from datetime import datetime
from enum import Enum
import dd2.utils.decorators as decorators

import cv2.cv2 as cv2
import numpy as np

import dd2.utils.enums as enums

wrapper_to_obj = {
    'numpy.ndarray': lambda data: np.array(data, dtype='float64')
}

# Directory handling
def names_from_directory(directory):
    return os.listdir(directory)

def paths_from_directory(directory):
    return [f"{directory}\\{image}" for image in os.listdir(directory)]

def images_from_directory(directory):
    return [cv2.imread(f"{directory}\\{image}") for image in os.listdir(directory)]

def get_path_from_prefix(prefix, directory, exact=False):
    if exact:
        filename = next(name for name in os.listdir(directory) if name == prefix)
    else:
        filename = next(name for name in os.listdir(directory) if name.startswith(prefix))
    return os.path.join(os.path.abspath(directory), filename)

def generate_path(directory, extension, filename=None):
    if not filename:
        prefix = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"{prefix}.{extension}"
    return os.path.join(os.path.abspath(directory), filename)

def _custom_encoder(obj):
    # Handle enumerations
    if issubclass(obj.__class__, Enum):
        dict_ = {'name': obj.name}
    elif issubclass(obj.__class__, np.ndarray):
        dict_ = {
            'data': obj.tolist(),
            '__wrapper__': 'numpy.ndarray'
        }
    elif hasattr(obj, 'to_json'):
        dict_ = obj.to_json()
    else:
        dict_ = obj.__dict__

    serializing_cls_name = obj.__class__.__dict__.get('__serializing_cls_name__')
    if serializing_cls_name:
        dict_['__serializing_cls_name__'] = serializing_cls_name
    return dict_

def _custom_decoder(dict_):
    # print(f"Decoding:\n {dict_}\n\n")
    serializing_cls_name = dict_.pop('__serializing_cls_name__', None)
    if serializing_cls_name:
        cls = decorators.name_to_class[serializing_cls_name]
        if hasattr(cls, 'from_json'):
            return getattr(cls, 'from_json')(dict_)
        if issubclass(cls, Enum):
            value = getattr(cls, dict_['name'])
            # print(f"Enum decoding\n Dict: {dict_}\n Value: {value}")
            return value
        return cls(**dict_)

    wrapper = dict_.pop('__wrapper__', None)
    if wrapper:
        obj = wrapper_to_obj[wrapper](**dict_)
        return obj
    return dict_


def load_json(prefix, directory, exact=False):
    path = get_path_from_prefix(prefix, directory, exact=exact)
    with open(path, "r") as f:
        return json.load(f, object_hook=_custom_decoder)

def dump_json(json_dict, directory, filename=None, indent=4):
    path = generate_path(directory, 'json', filename=filename)
    with open(path, "w") as f:
        json.dump(json_dict, f, default=_custom_encoder, indent=indent)

def rewrite_json(prefix, directory, exact=False, indent=4):
    json_dict = load_json(prefix, directory, exact=exact)
    return dump_json(json_dict, directory, filename=None, indent=indent)



# Image IO
def save_image(image, filename=None):
    path = generate_path(enums.Folder.IMAGES_DIR.value, 'png', filename=filename)
    cv2.imwrite(path, image)
    print(f"Saved image to: {path}")

def save_template(image, x, y, dx, dy):
    prefix = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    suffix = f"[{x},{y},{dx},{dy}]"
    filename = f"{prefix}__{suffix}"
    path = generate_path(enums.Folder.TEMPLATES_DIR.value, 'png', filename=filename)
    cv2.imwrite(path, image)
    print(f"Saved template to: {path}")


def load_from_images(prefix, exact=False):
    path = get_path_from_prefix(prefix, enums.Folder.IMAGES_DIR.value, exact=exact)
    return cv2.imread(path)

def load_from_templates(prefix, exact=False):
    path = get_path_from_prefix(prefix, enums.Folder.TEMPLATES_DIR.value, exact=exact)
    match = re.search(r'\[(\d+),(\d+),(\d+),(\d+)\]', path)
    x, y, dx, dy = (int(e) for e in match.groups())
    return cv2.imread(path), (x, y, dx, dy)
