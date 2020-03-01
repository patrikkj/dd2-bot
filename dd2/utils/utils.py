import time
from enum import Enum, auto

import cv2.cv2 as cv2

import dd2.io as io
import dd2.utils.text_search as text_search

from . import enums, templates


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

def get_hero_slot(hwnd):
    slot_1, slot_2, slot_3 = 0, 0, 0

    slot_1 += 1*int(compare_template(templates.SLOT_1_F1, hwnd, threshold=0.92))
    slot_1 += 2*int(compare_template(templates.SLOT_1_F2, hwnd, threshold=0.92))
    slot_2 += 2*int(compare_template(templates.SLOT_2_F2, hwnd, threshold=0.92))
    slot_2 += 3*int(compare_template(templates.SLOT_2_F3, hwnd, threshold=0.92))
    slot_3 += 3*int(compare_template(templates.SLOT_3_F3, hwnd, threshold=0.75)) # Bad template, should update
    slot_3 += 4*int(compare_template(templates.SLOT_3_F4, hwnd, threshold=0.92))
    _mapping = {
        (0, 0, 0): enums.Slot.HERO_1,
        (2, 0, 0): enums.Slot.HERO_1,
        (2, 3, 0): enums.Slot.HERO_1,
        (2, 3, 4): enums.Slot.HERO_1,

        (1, 0, 0): enums.Slot.HERO_2,
        (1, 3, 0): enums.Slot.HERO_2,
        (1, 3, 4): enums.Slot.HERO_2,

        (1, 2, 0): enums.Slot.HERO_3,
        (1, 2, 4): enums.Slot.HERO_3,

        (1, 2, 3): enums.Slot.HERO_4,
    }
    return _mapping.get((slot_1, slot_2, slot_3), enums.Slot.HERO_1)

def set_hero_slot(client, hero_slot):
    while get_hero_slot(client.hwnd) != hero_slot:
        io.keyboard.press_and_release(hero_slot.get_hotkey()) 
        cv2.waitKey(200) & 0xFF
    client.set_active_hero_slot(hero_slot)

def update_hero_slot(client):
    active_hero_slot = get_hero_slot(client.hwnd)
    client.set_active_hero_slot(active_hero_slot)

# Images
def extract_image_region_interactive(hwnd):
    io.win.set_focus_console()
    print("\nIMAGE EXTRACTION [2x HOME]")

     # Capture boundng box
    # print("Hover top left corner and press [HOME] ...")
    io.keyboard.wait("home") 
    x1, y1 = io.mouse.get_mouse_pos(hwnd=hwnd)

    # print("Hover bottom right corner and press [HOME] ...")
    io.keyboard.wait("home") 
    x2, y2 = io.mouse.get_mouse_pos(hwnd=hwnd)
    dx, dy = x2 - x1, y2 - y1

    image = io.screen.capture_region(x1, y1, dx, dy, hwnd=hwnd)
    io.file.save_template(image, x1, y1, dx, dy)

def _compare_images(image_1, image_2):
    return cv2.matchTemplate(image_1, image_2, cv2.TM_CCOEFF_NORMED)

def compare_region_with_template(template, x, y, dx, dy, hwnd):
    image = io.screen.capture_region(x, y, dx, dy, hwnd=hwnd)
    return _compare_images(image, template)

def compare_template(template_prefix, hwnd, threshold=0.8):
    template, window_details = io.file.load_from_templates(template_prefix, exact=False)
    res = compare_region_with_template(template, *window_details, hwnd)
    # print(f"Comparing '{template_prefix}'. Res: {res} Threshold: {threshold}")
    return res > threshold

def compare_until_threshold(template_prefix, hwnd, threshold=0.8):
    template, window_details = io.file.load_from_templates(template_prefix, exact=False)
    while (res := compare_region_with_template(template, *window_details, hwnd)) < threshold:
        cv2.waitKey(2) & 0xFF
        # print(f"Res: {res}")
    print(f"Comparison successful for [{template_prefix}, {threshold}] with result: {res}.")

def compare_until_threshold_fail(template_prefix, hwnd, threshold=0.8):
    template, window_details = io.file.load_from_templates(template_prefix, exact=False)
    while (res := compare_region_with_template(template, *window_details, hwnd)) > threshold:
        cv2.waitKey(2) & 0xFF
        # print(f"Res: {res}")
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


# Loops
def do_until(callable_, test, target_value=True, args=(), test_args=(), on_retry=lambda *_: None, retry=0.2, timeout=None):
    timeout = timeout if timeout else float("inf")
    start = time.perf_counter()
    call_count = 0
    while (time.perf_counter() - start) < timeout:
        call_count += 1
        callable_(*args)
        
        value = test(*test_args)
        test_count = 0
        print(f" ... Value: {value}, Target: {target_value} [{call_count,}, {test_count}]")
        if value == target_value:
            return True
        
        interval_start = time.perf_counter()
        while (time.perf_counter() - interval_start) < retry:
            test_count += 1
            value = test(*test_args)
            # print(f" ... Value: {value}, Target: {target_value}")
            if value == target_value:
                return True
            cv2.waitKey(2) & 0xFF
        on_retry()
    return False

def wait_until(predicate, *args, timeout=None):
    timeout = timeout if timeout else float("inf")
    start = time.perf_counter()
    if predicate(*args):
            return True
    while (time.perf_counter() - start) < timeout:
        if predicate(*args):
            return True
        cv2.waitKey(2) & 0xFF
    return False


def timeit(method):
    def timed(*args, **kw):
        ts = time.perf_counter()
        result = method(*args, **kw)
        te = time.perf_counter()
        diff = te - ts
        print(f"{method.__name__}: {diff:.8f} s")
        return result
    return timed
