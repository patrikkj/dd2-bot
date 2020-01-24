import cv2.cv2 as cv2
from . import text_search
from numpy import linspace


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
def extract_image_region_interactive(hwnd, options=None):
    print("\nIMAGE EXTRACTION")

     # Capture boundng box
    print("Hover top left corner and press [HOME] ...")
    keyboard.wait("home") 
    x1, y1 = mouse_io.get_mouse_pos(hwnd=hwnd)

    print("Hover bottom right corner and press [HOME] ...")
    keyboard.wait("home") 
    x2, y2 = mouse_io.get_mouse_pos(hwnd=hwnd)
    dx, dy = x2 - x1, y2 - y1

    image = capture_region(x1, y1, dx, dy, hwnd=hwnd)
    cv2.imwrite()
    print(f"Extracted text: {result}")


