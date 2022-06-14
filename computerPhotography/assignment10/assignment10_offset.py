import sys
import os
import numpy as np
import cv2


def offset_image(base_gray_image, image):
    translated_images = []

    sift = cv2.SIFT()

    gray_image = gray(image)
    base_keypoints, base_descriptors = sift.detectAndCompute(base_image, None)

    FLANN_INDEX_KDTREE = 0
    index_params = { 'algorithm':FLANN_INDEX_KDTREE, 'trees':5 }
    search_params = { 'checks':50 }
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    keypoints, descriptors = sift.detectAndCompute(gray_image, None)
    matches = flann.knnMatch(base_descriptors, descriptors, k=2)
    matches.sort(key=lambda y: y[0].distance/y[1].distance)

    src_tri = []
    dst_tri = []
    src_pt = np.array(keypoints[matches[0][0].trainIdx].pt)
    dst_pt = np.array(base_keypoints[matches[0][0].queryIdx].pt)

    translate = dst_pt - src_pt
    translate_mat = np.matrix([ [1.0, 0.0, translate[0]],
                                [0.0, 1.0, translate[1]]])
 
    translated_image = cv2.warpAffine(image, translate_mat, (base_image.shape[1], base_image.shape[0]))
    translated_image = np.uint8(translated_image)

    return translated_image


def load_translate_write(input_name, base_gray_image, output_name):
    image = cv2.imread(input_name)
    image = cv2.resize(image, (0,0), fx=0.25, fy=0.25, interpolation=cv2.INTER_LANCZOS4)
    translated_image = offset_image(base_gray_image, image)
    cv2.imwrite(output_name, translated_image)


def gray(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


if __name__ == "__main__":
    image_dir = "willrogers"
    output_dir = "willrogers_translated"
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    names = filter(lambda x: os.path.splitext(x)[1] in ['.png', '.jpg'],  os.listdir(image_dir))
    input_names = map(lambda x: os.path.join(image_dir, x), names)
    output_names = map(lambda x: os.path.join(output_dir, x), names)
    mid = len(input_names)/2
    base_image = cv2.imread(input_names[mid])
    base_image = cv2.resize(base_image, (0,0), fx=0.25, fy=0.25, interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(output_names[mid], base_image)

    base_gray_image = gray(base_image)
    for input_name, output_name in zip(input_names, output_names):
        if input_name == input_names[mid]:
            continue

        # translate images to mid_image
        load_translate_write(input_name, base_gray_image, output_name)
