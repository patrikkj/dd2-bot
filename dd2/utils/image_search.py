from os import listdir, path

import cv2.cv2 as cv2
import keyboard
import numpy as np
import win32gui
from PIL import ImageGrab

import dd2.io.file_io as file_io
from dd2.io.user_io import keyboard_io, mouse_io, user_io, win_io

WINDOW_NAME = "Images"


def image_search(image_path, template_path, threshold):
    return _image_search([image_path], [template_path], threshold)

def image_search_multi(image_dir, template_dir, threshold, image_filter=lambda _: True):
    image_paths = [f"{image_dir}\\{image}" for image in listdir(image_dir)]
    template_paths = [f"{template_dir}\\{template}" for template in listdir(template_dir)]
    return _image_search(image_paths, template_paths, threshold, image_filter=image_filter)

def region_search(x, y, width, height, template, threshold):
    return image_search(win_io.capture_region(x, y, width, height), template, threshold)

def screen_capture(width=1920, height=1080):
    return win_io.capture_region(0, 0, width, height)

#def template_search(image, template_dir, method=cv2.TM_CCOEFF_NORMED):

def masked_search(image, template_dir, mask_dir, method=cv2.TM_SQDIFF):
    # Prepare templates
    template_names = file_io.names_from_directory(template_dir)
    templates_bgr = file_io.images_from_directory(template_dir)
    templates_gray = [cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) for template in templates_bgr]

    # Prepare masks
    mask_names = file_io.names_from_directory(mask_dir)
    masks_bgr = file_io.images_from_directory(mask_dir)
    masks_gray = [cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY) for mask in masks_bgr]

    # Matching rectangle data
    match_dict = {}

    for template, template_name, mask, mask_name in zip(templates_gray, template_names, masks_gray, mask_names):
        # Fetch dimensions
        h, w, *_ = template.shape[:]

        # Template matching
        res = cv2.matchTemplate(image, template, method, mask=mask)

        #  # Display templates image
        # cv2.imshow("Template image", template)
        # key = cv2.waitKey(0)

        #  # Display mask image
        # cv2.imshow("Masked image", cv2.bitwise_and(template, template, mask = mask))
        # key = cv2.waitKey(0)

        # Find matching rectangle per template
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if (method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]):
            match_dict[template_name] = (min_val, min_loc)
        else:
            match_dict[template_name] = (max_val, max_loc)

    # Print rectangle data
    for template_name, match_data in match_dict.items():
        print(f"Template: {template_name:10} Value: {match_data[0]:10} Location: {match_data[1]}")

    if (method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]):
        bestfit_template, bestfit_data = min(match_dict.items(),key=lambda tup: tup[1][0])
    else:
        bestfit_template, bestfit_data = max(match_dict.items(),key=lambda tup: tup[1][0])
    
    # # Draw rectangle
    bestfit_val, bestfit_loc = bestfit_data
    print(f"Best fit: {bestfit_data}")
    print()

    # # Display results
    # cv2.rectangle(screen_rgb, bestfit_loc, (bestfit_loc[0] + w, bestfit_loc[1] + h), (0, 255, 255), thickness=5)
    # scaled_img = cv2.resize(screen_rgb, (0,0), fx=0.6,fy=0.6)
    # cv2.imshow("Screenshot", scaled_img)
    # key = cv2.waitKey(0)
    # cv2.destroyAllWindows()

def screen_search(template_dir, mask_dir, method=cv2.TM_SQDIFF):
    # Capture screen
    screen_bgr = np.array(screen_capture())
    screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
    return masked_search(screen_bgr, template_dir, mask_dir, method=method)

def _image_search(image_paths, template_paths, threshold,  image_filter=lambda _: True):
    # Pre-processing
    cv2.namedWindow(WINDOW_NAME)

    # Filter images
    image_paths_filtered = [image_path for image_path in image_paths if image_filter(path.basename(image_path))]

    for image_path in image_paths_filtered:
        # Load and process screenshot
        image_rgb = cv2.imread(image_path)
        image_gray = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2GRAY)
        # image_gray = cv2.GaussianBlur(image_gray, (3, 3), 0)

        # Perform template matching for every orientation
        matches = 0
        img_min_template, img_max_template = None, None
        img_min_val, img_max_val, img_min_loc, img_max_loc = float('inf'),  -float('inf'), None, None
        for template_path in template_paths:
            # Load template
            template = cv2.imread(template_path)

            template_name = path.basename(template_path)
            template_mask_path = template_path.replace(".png", "_mask.png")
            template_mask = cv2.imread(template_mask_path)

            _, w, h = template.shape[::-1]

            # Pattern matching
            #res = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
            method = cv2.TM_SQDIFF
            res = cv2.matchTemplate(image_rgb, template, method, mask=template_mask)

            # Filter based on threshold
            # print(res)
            # loc = np.where(res >= threshold)
            # pts = zip(*loc[::-1])

            # # Draw matching rectangles
            # matches += len(loc[0])
            # for pt in pts:
            #     cv2.rectangle(image_rgb, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 1)

            # Find matching rectangle per template
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if (method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]):
                if (min_val < img_min_val):
                    img_min_val = min_val
                    img_min_loc = min_loc
                    img_min_template = template_name
            else:
                if (max_val < img_max_val):
                    img_max_val = max_val
                    img_max_loc = max_loc
                    img_max_template = template_name


        # Extract rectangle data
        if (method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]):
            match_val = img_min_val
            match_loc = img_min_loc
            match_template = img_min_template
        else:
            match_val = img_max_val
            match_loc = img_max_loc
            match_template = img_max_template

        # Draw rectangle
        cv2.rectangle(image_rgb, match_loc, (match_loc[0] + w, match_loc[1] + h), (0, 255, 255), 1)

        # Post-processing
        scaled_img = cv2.resize(image_rgb, (0,0), fx=0.6,fy=0.6)
        cv2.putText(scaled_img, f"{path.basename(image_path)} ({matches} matches)", (10, 500), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (255, 255, 0))

        # Print iteration
        print(f"Image: {path.basename(image_path):10} Template: {match_template:10}  Match value: {match_val:15}")
        # print(f"Match value: {match_val}")
        # print(f"Image: {path.basename(image_path)}")
        # print(f"Total matches: {matches}\n")

        # Display results
        cv2.imshow(WINDOW_NAME, scaled_img)
        key = cv2.waitKey(0)
        if key == ord('q'):
            exit(0)
