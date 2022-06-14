import sys
import os
import numpy as np
import cv2

# http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_feature2d/py_feature_homography/py_feature_homography.html
def warp_image(base_image, image):
    sift = cv2.SIFT()
    FLANN_INDEX_KDTREE = 0
    index_params = { 'algorithm':FLANN_INDEX_KDTREE, 'trees':5 }
    search_params = { 'checks':50 }
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    base_keypoints, base_descriptors = sift.detectAndCompute(base_image, None)
    keypoints, descriptors = sift.detectAndCompute(image, None)
    matches = flann.knnMatch(base_descriptors, descriptors, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    source_points = []
    destination_points = []
    if len(good_matches) > 10:
        for match in good_matches:
            source_points.append(base_keypoints[match.queryIdx].pt)
            destination_points.append(keypoints[match.trainIdx].pt)
    else:
        print "Not enough good matches"

    source_array = np.float32(source_points).reshape(-1, 1, 2)
    destination_array = np.float32(destination_points).reshape(-1, 1, 2)

    M, mask = cv2.findHomography(destination_array, source_array, cv2.RANSAC, 5.0)
    warped_image = cv2.warpPerspective(image, M, (image.shape[1], image.shape[0]))

    return warped_image.astype(np.uint8)


def load_warp_write(scale, input_name, base_image, output_name):
    image = cv2.resize(cv2.imread(input_name), (0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_LANCZOS4)
    warped_image = warp_image(base_image, image)
    warped_image = cv2.resize(warped_image, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(output_name, warped_image)


if __name__ == "__main__":
    scale = 0.25
    image_dir = "willrogers"
    output_dir = "willrogers_tiny"
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    names = filter(lambda x: os.path.splitext(x)[1] in ['.png', '.jpg'],  os.listdir(image_dir))
    input_names = map(lambda x: os.path.join(image_dir, x), names)
    output_names = map(lambda x: os.path.join(output_dir, x), names)
    mid = len(input_names)/2
    base_image = cv2.resize(cv2.imread(input_names[mid]), (0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_LANCZOS4)
    base_image_resized = cv2.resize(base_image, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(output_names[mid], base_image_resized)

    for input_name, output_name in zip(input_names, output_names):
        if input_name == input_names[mid]:
            continue

        # warp images to mid_image
        load_warp_write(scale, input_name, base_image, output_name)
