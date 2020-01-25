from PIL import ImageGrab

# Screen capturing
def capture_screen():
    return ImageGrab.grab()

def capture_region(x, y, dx, dy):
    return ImageGrab.grab(bbox=(x, y, x + dx, y + dy))
