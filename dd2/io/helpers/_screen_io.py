from PIL import ImageGrab
import numpy as np

# Screen capturing
def capture_screen():
    return np.array(ImageGrab.grab().getdata(), dtype='uint8')

def capture_region(x, y, dx, dy):
    # image = ImageGrab.grab(bbox=(x, y, x + dx, y + dy))
    return np.array(ImageGrab.grab(bbox=(x, y, x + dx, y + dy)).convert('RGB'))
    # return np.array(image.getdata(), dtype='uint8').reshape((image.size[1], image.size[0], 3))
