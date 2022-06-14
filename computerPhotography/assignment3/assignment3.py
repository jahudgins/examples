# ASSIGNMENT 3
# Jonathan Hudgins (jhudgins8)
# GTID: 903050550

import cv2
import numpy as np
import argparse

def load_images(filenames, load_cropped, crop):
    cropped_filenames = map(lambda x: x + "_cropped.png", filenames)
    if load_cropped:
        images = map(lambda x: cv2.imread(x), cropped_filenames)
    else:
        images = map(cv2.imread, filenames)
        if crop:
            dims = map(int, crop.split(','))
            # for testing purposes crop to lower left
            cropped_images = map(lambda x: x[dims[2]:dims[2]+dims[3], dims[0]:dims[0]+dims[1],:], images)
            cropped_images = map(lambda x: cv2.resize(x, (dims[1]/4, dims[3]/4), interpolation=cv2.INTER_LANCZOS4), cropped_images)
            map(lambda x: cv2.imwrite(x[0], x[1]), zip(cropped_filenames, cropped_images))

            images = cropped_images

    return images


def outlier_blend(images):
    images = map(lambda x: x/255., images)
    shape = images[0].shape
    outlier_image = np.zeros((shape[0], shape[1], 3))

    y = 0
    while y < shape[0]:
        x = 0
        while x < shape[1]:
            total = np.zeros((3))
            for image in images:
                total += image[y, x, :]
            average = total / len(images)
            farthest = images[0][y, x, :]
            farthest_dist = np.linalg.norm(images[0][y, x, :] - average)
            for image in images[1:]:
                dist = np.linalg.norm(image[y, x, :] - average)
                if dist > farthest_dist:
                    farthest_dist = dist
                    farthest = image[y, x, :]

            try:
                outlier_image[y, x, :] = farthest
            except Exception as ex:
                print y, x
                print outlier_image[y, x, :]
                print farthest
                raise

            x += 1
        y += 1

    return np.uint8(outlier_image * 255)


def warp_images(images):
    warpped_images = [images[0]]
    base_image = images[0]
    images = images[1:]

    sift = cv2.SIFT()

    base_keypoints, base_descriptors = sift.detectAndCompute(base_image, None)

    FLANN_INDEX_KDTREE = 0
    index_params = { 'algorithm':FLANN_INDEX_KDTREE, 'trees':5 }
    search_params = { 'checks':50 }
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    for image in images:
        keypoints, descriptors = sift.detectAndCompute(image, None)
        matches = flann.knnMatch(base_descriptors, descriptors, k=2)
        matches.sort(key=lambda y: y[0].distance/y[1].distance)

        src_tri = []
        dst_tri = []
        index = 0
        while len(src_tri) < 3:
            skip = False
            src_pt = np.array(keypoints[matches[index][0].trainIdx].pt)
            dst_pt = np.array(base_keypoints[matches[index][0].queryIdx].pt)
            for pt in src_tri:
                if np.linalg.norm(pt - src_pt) < 10:
                    skip = True

            if not skip:
                src_tri.append(src_pt)
                dst_tri.append(dst_pt)

            index += 1
        
        src_tri = np.float32(src_tri)
        dst_tri = np.float32(dst_tri)
        transform = cv2.getAffineTransform(src_tri, dst_tri)
        warpped_image = cv2.warpAffine(image, transform, (base_image.shape[1], base_image.shape[0]))
        warpped_image = np.uint8(warpped_image)
        warpped_images.append(warpped_image)

    return warpped_images


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select the outlier pixels')
    parser.add_argument('--crop', '-c', help="crop and save as cropped png's")
    parser.add_argument('--load_cropped', '-l', action='store_true', help="load the cropped png's")
    parser.add_argument('--filenames', '-f', nargs='+', help="load the cropped png's")
    args = parser.parse_args()

    #import pdb; pdb.set_trace()
    #filenames = ["20150124_095727.jpg", "20150124_095729.jpg", "20150124_095730.jpg",
    #            "20150124_095732.jpg", "20150124_095733.jpg", "20150124_095735.jpg"]
    #filenames = ["20150124_095727.jpg", "20150124_095729.jpg", "20150124_095730.jpg"]
    images = load_images(args.filenames, args.load_cropped, args.crop)
    warpped_images = warp_images(images)

    map(lambda x: cv2.imwrite(x[0]+"_warpped.png", x[1]), zip(args.filenames, warpped_images))

    outlier_image = outlier_blend(warpped_images)

    cv2.imwrite('outlier.png', outlier_image)

    cv2.imshow('outlier.png', outlier_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


