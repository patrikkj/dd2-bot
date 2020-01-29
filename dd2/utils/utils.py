import numpy as np
import cv2.cv2 as cv2
from enum import Enum, auto
from dd2.io import file_io, keyboard_io, mouse_io, screen_io, win_io
from dd2.io.helpers import _file_io, _keyboard_io, _mouse_io, _screen_io, _win_io
import dd2.utils.text_search as text_search

class Field(Enum):
    DU = auto()
    WAVE_COUNT = auto()
    MOB_COUNT = auto()

DU, WAVE, MOB_COUNT = Field.DU, Field.WAVE_COUNT, Field.MOB_COUNT
DU_FIELD = (1150, 106, 70, 17)
WAVE_FIELD = (1130, 35, 40, 20)
MOB_FIELD = (1200, 42, 46, 38)



# Text 
def get_DU(hwnd):
    x, y, dx, dy = DU_FIELD
    options = {
        'plot_histogram': False,

        'apply_range_mask': True,
        'display_range_mask': False,
        'mask_range_lower': 100,
        'mask_range_upper': 255,

        'resize_scale_x': 2,
        'resize_scale_y': 2,

        'apply_dilation': False, 
        'apply_erosion': False,

        'apply_gaussian_blur': False, 
        'gaussian_blur_ksize': 5, 
        'apply_bilateral_filter': False,

        'apply_threshold': True,
        'threshold_lbound': 100,
        'threshold_ubound': 255,

        'apply_border': True,

        'display_processed': False,

        'config_digits': True
    }
    try:
        raw_text = text_search.extract_text_region(x, y, dx, dy, hwnd=hwnd, options=options)
        raw_text = raw_text.replace(',', '').replace('.', '').replace(' ', '')
        current, cap = (int(num) for num in raw_text.split("/"))
        return current, cap
    except:
        return -1, -1

def get_wave_count(hwnd):
    x, y, dx, dy = WAVE_FIELD
    options = {
        'plot_histogram': False,

        'apply_range_mask': True,
        'display_range_mask': False,
        'mask_range_lower': 127,
        'mask_range_upper': 255,

        'resize_scale_x': 1.2,
        'resize_scale_y': 1.2,

        'apply_dilation': True, 
        'apply_erosion': True,

        'apply_gaussian_blur': False, 
        'gaussian_blur_ksize': 5, 
        'apply_bilateral_filter': False,

        'apply_threshold': True,
        'threshold_lbound': 127,
        'threshold_ubound': 255,

        'apply_border': True,

        'display_processed': False,

        'config_digits': True
    }
    try:
        raw_text = text_search.extract_text_region(x, y, dx, dy, hwnd=hwnd, options=options)
        raw_text = raw_text.replace(',', '').replace('.', '').replace(' ', '')
        current, total = (int(num) for num in raw_text.split("/"))
        return current, total
    except:
        return -1, -1

def get_mob_count(hwnd):
    x, y, dx, dy = MOB_FIELD
    options = {
        'plot_histogram': False,

        'apply_range_mask': True,
        'display_range_mask': False,
        'mask_range_lower': 150,
        'mask_range_upper': 255,

        'resize_scale_x': 1,
        'resize_scale_y': 1,

        'apply_dilation': True, 
        'apply_erosion': True,

        'apply_gaussian_blur': False, 
        'gaussian_blur_ksize': 5, 
        'apply_bilateral_filter': False,

        'apply_threshold': True,
        'threshold_lbound': 150,
        'threshold_ubound': 255,

        'apply_border': True,

        'display_processed': False,

        'config_digits': True
    }
    try:
        raw_text = text_search.extract_text_region(x, y, dx, dy, hwnd=hwnd, options=options)
        return int(raw_text)
    except:
        return -1
    # raw_text = raw_text.replace(',', '').replace('.', '').replace(' ', '')
    # current, total = (int(num) for num in raw_text.split("/"))
    # return current, total


# Images
def extract_image_region_interactive(hwnd):
    win_io.set_focus_console()
    print("\nIMAGE EXTRACTION [2x HOME]")

     # Capture boundng box
    # print("Hover top left corner and press [HOME] ...")
    keyboard_io.wait("home") 
    x1, y1 = mouse_io.get_mouse_pos(hwnd=hwnd)

    # print("Hover bottom right corner and press [HOME] ...")
    keyboard_io.wait("home") 
    x2, y2 = mouse_io.get_mouse_pos(hwnd=hwnd)
    dx, dy = x2 - x1, y2 - y1

    image = screen_io.capture_region(x1, y1, dx, dy, hwnd=hwnd)
    file_io.save_template(image, x1, y1, dx, dy)

def _compare_images(image_1, image_2):
    # print(f"Dim 1: {image_1.shape}")
    # print(f"Dim 2: {image_2.shape}")
    # cv2.imshow("Win 1", image_1)
    # cv2.imshow("Win 2", image_2)
    # cv2.waitKey(0)
    # print("IM1",image_1)
    # print("IM2",image_2)
    return cv2.matchTemplate(image_1, image_2, cv2.TM_CCOEFF_NORMED)

def compare_region_with_template(template, x, y, dx, dy, hwnd):
    image = screen_io.capture_region(x, y, dx, dy, hwnd=hwnd)
    return _compare_images(image, template)

def compare_template(template_prefix, hwnd, threshold=0.8):
    template, window_details = file_io.load_from_templates(template_prefix, exact=False)
    res = compare_region_with_template(template, *window_details, hwnd)
    return res > threshold

def compare_until_threshold(template_prefix, hwnd, threshold=0.8):
    template, window_details = file_io.load_from_templates(template_prefix, exact=False)
    while (res := compare_region_with_template(template, *window_details, hwnd)) < threshold:
        cv2.waitKey(2) & 0xFF
        print(f"Res: {res}")
    print(f"Comparison successful for [{template_prefix}, {threshold}] with result: {res}.")

def compare_until_threshold_fail(template_prefix, hwnd, threshold=0.8):
    template, window_details = file_io.load_from_templates(template_prefix, exact=False)
    while (res := compare_region_with_template(template, *window_details, hwnd)) > threshold:
        cv2.waitKey(2) & 0xFF
        print(f"Res: {res}")
    print(f"Comparison fail successful for [{template_prefix}, {threshold}] with result: {res}.")

def read_field_until_value(field, value, hwnd):
    if field == Field.DU:
        callable_ = get_DU
    elif field == Field.WAVE_COUNT:
        callable_ = get_wave_count
    elif field == Field.MOB_COUNT:
        callable_ = lambda hwnd: (get_mob_count(hwnd), )
    while (output := callable_(hwnd)[0]) != value:
        print(f"Field: {field}, Current: {output}, Target: {value}")
        cv2.waitKey(5) & 0xFF
