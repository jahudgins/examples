# Problem Set 4
# Jonathan Hudgins (jhudgins8)
# CS4495 Spring 2015 OMS
# GTID: 903050550

import cv2
import numpy as np
import argparse
import scipy.ndimage
import scipy.signal
import math
import sys
import random


def gaussian(sigma, size):
    m = np.zeros((size, size))
    m[size/2, size/2] = 1
    return scipy.ndimage.gaussian_filter(m, sigma)


def stack_gradient_pair(img):
    sobelx = cv2.Sobel(img, cv2.CV_8U, 1, 0, ksize=3)
    sobely = cv2.Sobel(img, cv2.CV_8U, 0, 1, ksize=3)
    result = np.hstack((sobelx, sobely))
    result = np.absolute(result)
    return result


def harris(image, alpha, size):
    gaussian_matrix = gaussian(1, size)

    sobelx = cv2.Sobel(image, cv2.CV_8U, 1, 0, ksize=3)
    sobely = cv2.Sobel(image, cv2.CV_8U, 0, 1, ksize=3)
    sobelx = sobelx.astype(np.float)
    sobely = sobely.astype(np.float)

    #                  [ Ix^2    IxIy ]
    # M = sum ( w(x,y) [              ] )
    #      x,y         [ IxIy    Iy^2 ]
    #
    #
    # R = det(M) - alpha * trance(M)^2
    #

    ixSquared = np.multiply(sobelx, sobelx)
    iySquared = np.multiply(sobely, sobely)
    ixy = np.multiply(sobelx, sobely)

    m11 = scipy.signal.convolve2d(ixSquared, gaussian_matrix, mode='same', boundary='wrap')
    m12 = scipy.signal.convolve2d(ixy, gaussian_matrix, mode='same', boundary='wrap')
    m22 = scipy.signal.convolve2d(iySquared, gaussian_matrix, mode='same', boundary='wrap')
    det = np.multiply(m11, m22) - np.multiply(m12, m12)
    trace = m11 + m22
    R = det - alpha * np.multiply(trace, trace)

    return R, sobely, sobely


def normalize_image(image):
    max_value = image.max()
    min_value = image.min()
    image = (image - min_value) / (max_value - min_value)
    return image


def non_max_suppress(image, size):
    # get max value of each block
    domain = np.ones((size, size))
    local_maxes = scipy.signal.order_filter(image, domain, size * size - 1)
    result = np.copy(image)
    result[result != local_maxes] = 0.0
    result[result > 0.0] = 1.0
    return result
    

def overlay_corners(input_image, non_max_suppressed_image):
    line_magnitude = 12
    # change to a colored image
    overlayed = cv2.cvtColor(input_image, cv2.COLOR_GRAY2RGB)

    # loop through indices that are non-zero
    index_list = np.where(non_max_suppressed_image > 0)
    for indices in zip(*index_list):
        x = indices[1]
        y = indices[0]
        cv2.circle(overlayed, (x, y), radius=4, color=(0, 0, 255), thickness=2)
    return overlayed


def compute_relative_angles(gradienty, gradientx, local_region_size):
    absolute_angles = np.arctan2(gradienty, gradientx)
    window = np.ones((local_region_size, local_region_size))
    window = window / window.size
    average_angles = scipy.signal.convolve2d(absolute_angles, window, mode='same', boundary='wrap')
    relative_angles = absolute_angles - average_angles
    return relative_angles


def generate_keypoints(non_max_suppressed_image, angles, local_region_size):
    index_list = np.where(non_max_suppressed_image > 0)
    key_points = list()
    for indices in zip(*index_list):
        x = indices[1]
        y = indices[0]
        angle = angles[y, x]
        key_points.append(cv2.KeyPoint(x, y, _size=local_region_size, _angle=angle*180/math.pi, _octave=0))
    return key_points


def draw_matches(input_color_src, input_color_dst, matches, points_src, points_dst):
    matches_image = np.hstack((input_color_src, input_color_dst))
    for match in matches:
        point_src = points_src[match.queryIdx]
        point_dst = points_dst[match.trainIdx]
        src_tuple = (int(point_src.pt[0]), int(point_src.pt[1]))
        dst_tuple = (int(point_dst.pt[0]) + input_color_src.shape[1], int(point_dst.pt[1]))
        cv2.line(matches_image, src_tuple, dst_tuple, color=(0,255,0), thickness=1)

    return matches_image


def get_match_delta(points_src, points_dst, match):
    point_src = points_src[match.queryIdx]
    point_dst = points_dst[match.trainIdx]
    x_delta = point_dst.pt[0] - point_src.pt[0]
    y_delta = point_dst.pt[1] - point_src.pt[1]
    return np.array([x_delta, y_delta])


def ransac_translation(points_src, points_dst, matches):
    r = 0
    sigma = 5
    residuals = list()
    while r < 40:
        candidate_match = random.choice(matches)
        candidate_delta = get_match_delta(points_src, points_dst, candidate_match)
        total_residual = 0
        for match in matches:
            delta = get_match_delta(points_src, points_dst, match)
            error = np.linalg.norm(delta - candidate_delta)
            residual = error ** 2 / (sigma ** 2 + error ** 2)
            total_residual += residual

        residuals.append([total_residual, candidate_match])
        r += 1

    best_residual = min(residuals, key=lambda x: x[0])

    best_delta = get_match_delta(points_src, points_dst, best_residual[1])

    def test_error(match):
        delta = get_match_delta(points_src, points_dst, match)
        return np.linalg.norm(delta - best_delta)
        
    consensus_set = filter(lambda x: test_error(x) < 10, matches)
    return best_delta, consensus_set


def ransac_similarity(points_src, points_dst, matches):
    def similarity_error(transform, match):
        # get homogenous src and dst points for match
        src_pt = np.array(points_src[match.queryIdx].pt + (1,))
        dst_pt = np.array(points_dst[match.trainIdx].pt)

        # transform the src_pt
        transformed = np.dot(matching_transform, src_pt) 

        error = np.linalg.norm(transformed - dst_pt)
        return error

    r = 0
    sigma = 5
    similarity_threshold = 5
    best_residual = sys.float_info.max
    while r < 40:
        candidate_match1 = random.choice(matches)
        candidate_match2 = random.choice(matches)
        if candidate_match1 == candidate_match2:
            continue

        # solve for a, b, c, d in:
        #               [ u ]
        #  [ a -b c ]   [ v ]
        #  [ b  a d ]   [ 1 ]
        #
        # rewriting in terms of two candidate matches (u0, v0), (u1, v1)
        #
        #  [ u0 -v0  1  0  -x0 ]   [ a ]
        #  [ v0  u0  0  1  -y0 ]   [ b ]
        #  [ u1 -v1  1  0  -x1 ]   [ c ]
        #  [ v1  u1  0  1  -y1 ]   [ d ]
        #                          [ 1 ]
        #

        uv0 = points_src[candidate_match1.queryIdx].pt
        xy0 = points_dst[candidate_match1.trainIdx].pt
        uv1 = points_src[candidate_match2.queryIdx].pt
        xy1 = points_dst[candidate_match2.trainIdx].pt
        parameter_matrix =  np.matrix([  [ uv0[0], -uv0[1], 1, 0, -xy0[0]],
                                        [ uv0[1],  uv0[0], 0, 1, -xy0[1]],
                                        [ uv1[0], -uv1[1], 1, 0, -xy1[0]],
                                        [ uv1[1],  uv1[0], 0, 1, -xy1[1]]])
        U, s, V = np.linalg.svd(parameter_matrix)

        normalizedV =  V[-1,:]/V[-1,-1]
        [a, b, c, d, e] = normalizedV.tolist()[0]
        matching_transform = np.matrix([[a, -b, c],
                                        [b,  a, d]])

        total_residual = 0
        threshold_matches = list()
        for match in matches:
            error = similarity_error(matching_transform, match)
            residual = error ** 2 / (sigma ** 2 + error ** 2)
            total_residual += residual
            if error < similarity_threshold:
                threshold_matches.append(match)

        if total_residual < best_residual:
            best_residual = total_residual
            best_threshold_matches = threshold_matches
            best_matching_transform = matching_transform

        r += 1

    return best_matching_transform, best_threshold_matches

def part1():
    # read images
    img_transA = cv2.imread('input/transA.jpg', cv2.IMREAD_GRAYSCALE)
    img_simA = cv2.imread('input/simA.jpg', cv2.IMREAD_GRAYSCALE)

    # output images
    cv2.imwrite('output/ps4-1-a-1.png', stack_gradient_pair(img_transA))
    cv2.imwrite('output/ps4-1-a-2.png', stack_gradient_pair(img_simA))


def part1bc():
    alpha = 0.06
    threshold = 0.5
    local_region_size = 7
    filenames = [
        ['check', 'input/check.bmp', 'output/check-harris.png', 'output/check-corners.png'],
        ['check_rot', 'input/check_rot.bmp', 'output/check_rot-harris.png', 'output/check_rot-corners.png'],
        ['transA', 'input/transA.jpg', 'output/ps4-1-b-1.png', 'output/ps4-1-c-1.png'],
        ['transB', 'input/transB.jpg', 'output/ps4-1-b-2.png', 'output/ps4-1-c-2.png'],
        ['simA', 'input/simA.jpg', 'output/ps4-1-b-3.png', 'output/ps4-1-c-3.png'],
        ['simB', 'input/simB.jpg', 'output/ps4-1-b-4.png', 'output/ps4-1-c-4.png'],
    ]

    input_images = dict()
    key_points_dict = dict()
    for key, infile, outfile, cornerfile in filenames:
        input_image = cv2.imread(infile, cv2.IMREAD_GRAYSCALE)
        input_images[key] = input_image
        harris_values, gradientx, gradienty = harris(input_image, alpha, 5)
        normalized_image = normalize_image(harris_values)

        cv2.imwrite(outfile, (normalized_image * 255.).astype(np.uint8))

        actual_threshold = max(threshold, np.median(normalized_image) * 1.15)
        threshold_image = np.copy(normalized_image)
        threshold_image[threshold_image<actual_threshold] = 0
        non_max_suppressed_image = non_max_suppress(threshold_image, local_region_size)

        overlayed = overlay_corners(input_image, non_max_suppressed_image)
        cv2.imwrite(cornerfile, overlayed)

        # part2
        angles = compute_relative_angles(gradienty, gradientx, local_region_size)
        key_points = generate_keypoints(non_max_suppressed_image, angles, local_region_size)
        key_points_dict[key] = key_points

    paired_filenames = [
        ['check', 'check_rot', 'output/check_angles.png', 'output/matches.png'],
        ['transA', 'transB', 'output/ps4-2-a-1.png', 'output/ps4-2-b-1.png'],
        ['simA', 'simB', 'output/ps4-2-a-2.png', 'output/ps4-2-b-2.png'],
    ]

    sift = cv2.SIFT()
    bfm = cv2.BFMatcher()
    for key_src, key_dst, outfile, matches_file in paired_filenames:
        input_color_src = cv2.cvtColor(input_images[key_src], cv2.COLOR_GRAY2RGB)
        input_color_dst = cv2.cvtColor(input_images[key_dst], cv2.COLOR_GRAY2RGB)
        keypoint_image_src = cv2.drawKeypoints(input_color_src,
                                                key_points_dict[key_src],
                                                color=(0,0,255),
                                                flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        keypoint_image_dst = cv2.drawKeypoints(input_color_dst,
                                                key_points_dict[key_dst],
                                                color=(0,0,255),
                                                flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        keypoint_image = np.hstack((keypoint_image_src, keypoint_image_dst))
        cv2.imwrite(outfile, keypoint_image)

        points_src, descriptor_src = sift.compute(input_images[key_src], key_points_dict[key_src])
        points_dst, descriptor_dst = sift.compute(input_images[key_dst], key_points_dict[key_dst])
        matches = bfm.match(descriptor_src, descriptor_dst)

        matches_image = draw_matches(input_color_src, input_color_dst, matches, points_src, points_dst)
        cv2.imwrite(matches_file, matches_image)


        # now get a RANSAC consensus for translation images
        if key_src == 'transA':
            translation, consensus_set = ransac_translation(points_src, points_dst, matches)
            consensus_image = draw_matches(input_color_src, input_color_dst, consensus_set, points_src, points_dst)
            cv2.imwrite('output/ps4-3-b-1.png', consensus_image)
            print "translation: {}".format(translation)
            print "translation percent: {:.1f}%".format(100*len(consensus_set)/float(len(matches)))
            print

        if key_src == 'simA':
            similarity_matrix, consensus_set = ransac_similarity(points_src, points_dst, matches)
            consensus_image = draw_matches(input_color_src, input_color_dst, consensus_set, points_src, points_dst)
            cv2.imwrite('output/ps4-3-b-2.png', consensus_image)
            print "similarity matrix:"
            print similarity_matrix
            print "similarity percent: {:.1f}%".format(100*len(consensus_set)/float(len(matches)))
            print

    
if __name__ == '__main__':
    part1()
    part1bc()


