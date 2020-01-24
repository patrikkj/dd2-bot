import os
import cv2.cv2 as cv2

# Directory handling
def names_from_directory(directory):
    return os.listdir(directory)

def paths_from_directory(directory):
    return [f"{directory}\\{image}" for image in os.listdir(directory)]

def images_from_directory(directory):
    return [cv2.imread(f"{directory}\\{image}") for image in os.listdir(directory)]