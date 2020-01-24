import cv2.cv2 as cv2
import keyboard
import numpy as np
import pytesseract
from PIL import Image
from matplotlib import pyplot as plt
# from pytesseract import Output, image_to_string
from dd2.io.user_io import win_io, mouse_io


def _rescale():
    pass

def _extract_text(image, options=None):
    _options = {
        'plot_histogram': False,

        'apply_range_mask': True,
        'display_range_mask': False,
        'mask_range_lower': 100,
        'mask_range_upper': 255,

        'resize_scale_x': 1.0,
        'resize_scale_y': 1.0,

        'apply_dilation': True, 
        'apply_erosion': True,

        'apply_gaussian_blur': True, 
        'gaussian_blur_ksize': 5, 
        'apply_bilateral_filter': True,

        'apply_threshold': True,
        'threshold_lbound': 127,
        'threshold_ubound': 255,

        'apply_border': True,

        'display_processed': True,

        'config_digits': True,

    }
    if options:
        _options.update(options)

    # Convert to numpy array
    image = np.array(image, dtype='uint8')

    # Plot histogram
    if _options['plot_histogram']:
        plt.hist(image.ravel(), 256, [0, 256]) 
        plt.show()

    # Range masking
    if _options['apply_range_mask']:
        lower = np.array(3*[int(_options['mask_range_lower'])])
        upper = np.array(3*[_options['mask_range_upper']])
        mask = cv2.inRange(image, lower, upper)
        image = cv2.bitwise_and(image, image, mask=mask)

        if _options['display_range_mask']:
            cv2.imshow('Range mask', image)

    # Convert to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Rescale
    image = cv2.resize(image, None, fx=_options['resize_scale_x'], fy=_options['resize_scale_y'], interpolation=cv2.INTER_CUBIC)

    # # Apply dilation and erosion to remove some noise
    if _options['apply_dilation']:
        image = cv2.dilate(image, (1, 1), iterations=1)

    if _options['apply_erosion']:
        image = cv2.erode(image, (1, 1), iterations=1)

    # Apply blur to smooth out the edges
    if _options['apply_gaussian_blur']:
        image = cv2.GaussianBlur(image, 2*(_options['gaussian_blur_ksize'], ), 0).astype('uint8')

    if _options['apply_bilateral_filter']:
        image = cv2.bilateralFilter(image, 9, 75, 75)

    # Apply threshold to get image with only b&w (binarization)
    if _options['apply_threshold']:
        image = cv2.threshold(image, _options['threshold_lbound'], _options['threshold_ubound'], cv2.THRESH_BINARY_INV)[1]
    # image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

    # Create border around image to add some space
    if _options['apply_border']:
        image = cv2.copyMakeBorder(image, top=10, bottom=10, left=10, right=10, borderType=cv2.BORDER_CONSTANT, value=255)

    # Save the filtered image in the output directory
    if _options['display_processed']:
        cv2.imshow("Processed image", image)

    # Recognize text with tesseract for python
    # return pytesseract.image_to_string(image, config='digits')
    if _options['config_digits']:
        # return pytesseract.image_to_string(image, config='tessedit_char_whitelist="0123456789,/ "')
        return pytesseract.image_to_string(image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789/,.')
    else:
        return pytesseract.image_to_string(image, lang="eng")

def extract_text_region(x, y, dx, dy, hwnd=None, options=None):
    if hwnd:
        return _extract_text(win_io.capture_region(x, y, dx, dy, hwnd=hwnd), options=options)
    return _extract_text(win_io.capture_region(x, y, dx, dy), options=options)

def extract_text_file(relative_filepath, options=None):
    return _extract_text(Image.open(relative_filepath), options=options)

def extract_text_region_interactive(hwnd, options=None):
    print("\nTEXT RECOGNITION")

     # Capture boundng box
    print("Hover top left corner and press [HOME] ...")
    keyboard.wait("home") 
    x1, y1 = mouse_io.get_mouse_pos(hwnd=hwnd)

    print("Hover bottom right corner and press [HOME] ...")
    keyboard.wait("home") 
    x2, y2 = mouse_io.get_mouse_pos(hwnd=hwnd)
    dx, dy = x2 - x1, y2 - y1

    result = extract_text_region(x1, y1, dx, dy, hwnd=hwnd, options=options)
    print(f"Extracted text: {result}")

def extract_text_region_interactive_screen(options=None):
    print("\nTEXT RECOGNITION")

     # Capture boundng box
    print("Hover top left corner and press [HOME] ...")
    keyboard.wait("home") 
    x1, y1 = mouse_io.get_mouse_pos()

    print("Hover bottom right corner and press [HOME] ...")
    keyboard.wait("home") 
    x2, y2 = mouse_io.get_mouse_pos()
    dx, dy = x2 - x1, y2 - y1

    result = extract_text_region(x1, y1, dx, dy, options=options)
    print(f"Extracted text: {result}")


# Search untils
