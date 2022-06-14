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


# this factor of 10 seems necessary to make the flow map work
k_flow_scale = 10

def histogram(img):
    hist = []
    prev_count = 0
    for test_value in np.linspace(img.min(), img.max(), 11):
        test_count = len(np.where(img < test_value)[0])
        hist.append((test_value, test_count - prev_count))
        prev_count = test_count
    return hist


def lk_optic_flow(image1, image2, size):
    image1 = image1.astype(np.float)
    image2 = image2.astype(np.float)
    sum_matrix = np.ones((size, size))

    gradient_x = cv2.Sobel(image1, cv2.CV_8U, 1, 0, ksize=3).astype(np.float)
    gradient_y = cv2.Sobel(image1, cv2.CV_8U, 0, 1, ksize=3).astype(np.float)
    gradient_t = (image1 - image2).astype(np.float)

    ixx = np.multiply(gradient_x, gradient_x)
    iyy = np.multiply(gradient_y, gradient_y)
    ixy = np.multiply(gradient_x, gradient_y)
    ixt = np.multiply(gradient_x, gradient_t)
    iyt = np.multiply(gradient_y, gradient_t)

    m11 = scipy.signal.convolve2d(ixx, sum_matrix, mode='same', boundary='wrap')
    m12 = scipy.signal.convolve2d(ixy, sum_matrix, mode='same', boundary='wrap')
    m22 = scipy.signal.convolve2d(iyy, sum_matrix, mode='same', boundary='wrap')
    c1 = -scipy.signal.convolve2d(ixt, sum_matrix, mode='same', boundary='wrap')
    c2 = -scipy.signal.convolve2d(iyt, sum_matrix, mode='same', boundary='wrap')

    #  A =  [m11 m12]
    #       [m12 m22]
    #
    #  A-1 = 1/ det(A)  * [m22 -m12]
    #                     [-m12 m11]
    det = np.multiply(m11, m22) - np.multiply(m12, m12)
    with np.errstate(divide='ignore'):
        invalid = np.where(det == 0)
        invdet = 1 / det
        invdet[invalid] = 0

    u = np.multiply(invdet, (np.multiply(m22, c1) - np.multiply(m12, c2)))
    v = np.multiply(invdet, (np.multiply(m11, c2) - np.multiply(m12, c1)))

    return [u.astype(np.float32), v.astype(np.float32)]


def normalize_image(image):
    max_value = image.max()
    min_value = image.min()
    image = (image - min_value) / (max_value - min_value)
    return image


def draw_uv(filename, uv):
    image = np.hstack(uv)
    image = (normalize_image(image) * 255).astype(np.uint8)
    cv2.imwrite(filename, image)


def analyze_optic_flow(src_img, test_filename, output_filename):
    test_img = cv2.imread(test_filename, cv2.IMREAD_GRAYSCALE)
    uv = lk_optic_flow(src_img, test_img, 23)
    draw_uv(output_filename, uv)


# generatingKernel, reduce, gaussPyramid were taken from code I wrote for computer photography class

def generatingKernel(parameter):
    kernel = np.array([0.25 - parameter / 2.0, 0.25, parameter, 0.25, 0.25 - parameter /2.0])
    return np.outer(kernel, kernel)


def reduce(image):
    kernel = generatingKernel(0.4)
    convolved = scipy.signal.convolve2d(image, kernel, 'same')
    subsample = convolved[np.ix_(range(0,image.shape[0],2), range(0,image.shape[1],2))]
    return subsample


def expand(image):
    expanded = np.kron(image, np.matrix([[1., 0.], [0., 0.]]))
    kernel = generatingKernel(0.4)
    convolved = 4 * scipy.signal.convolve2d(expanded, kernel, 'same')

    return convolved


def gaussPyramid(image, levels):
    output = [image]
    while levels > 1 and min(image.shape) > 1:
        image = reduce(image)
        output.append(image)
        levels -= 1

    return output


def laplPyramid(gaussPyr):
    output = []

    idx = 0
    while idx < len(gaussPyr) - 1:
        expanded = expand(gaussPyr[idx+1])
        cropped = expanded[0:gaussPyr[idx].shape[0], 0:gaussPyr[idx].shape[1], ...]
        output.append(gaussPyr[idx] - cropped)
        idx += 1

    output.append(gaussPyr[-1])

    return output
 

def lk_warp_test(input_filename_1, input_filename_2):
    g_pyramid_1 = gaussPyramid(cv2.imread(input_filename_1, cv2.IMREAD_GRAYSCALE), 4)
    g_pyramid_2 = gaussPyramid(cv2.imread(input_filename_2, cv2.IMREAD_GRAYSCALE), 4)

    top_shape = g_pyramid_1[0].shape
    top_img_2 = g_pyramid_2[0]
    for count, (img_1, img_2) in enumerate(zip(g_pyramid_1, g_pyramid_2)):
        flow = lk_optic_flow(img_1, img_2, 23)
        img_2_mapped_to_1 = flow_warp(img_2, flow)
        cv2.imwrite('test/i-{}-a.png'.format(count), img_1)
        cv2.imwrite('test/i-{}-b.png'.format(count), img_2_mapped_to_1)

        for expansion in range(count):
            flow[0] = expand(2 * flow[0])
            flow[1] = expand(2 * flow[1])

        flow[0] = flow[0][0:top_shape[0], 0:top_shape[1], ...]
        flow[1] = flow[1][0:top_shape[0], 0:top_shape[1], ...]
        img_2_mapped_to_1_top = flow_warp(top_img_2, flow)
        cv2.imwrite('test/prime-{}.png'.format(count), img_2_mapped_to_1_top)


def lk_warp_level(input_filename_1, input_filename_2, level, flow_filename, difference_filename):
    g_pyramid_1 = gaussPyramid(cv2.imread(input_filename_1, cv2.IMREAD_GRAYSCALE), 4)
    g_pyramid_2 = gaussPyramid(cv2.imread(input_filename_2, cv2.IMREAD_GRAYSCALE), 4)

    top_shape = g_pyramid_1[0].shape
    top_img_2 = g_pyramid_2[0]
    img_1 = g_pyramid_1[level]
    img_2 = g_pyramid_2[level]

    flow = lk_optic_flow(img_1, img_2, 23)
    img_2_mapped_to_1 = flow_warp(img_2, flow)

    for expansion in range(level):
        flow[0] = expand(2 * flow[0])
        flow[1] = expand(2 * flow[1])

    flow[0] = flow[0][0:top_shape[0], 0:top_shape[1], ...]
    flow[1] = flow[1][0:top_shape[0], 0:top_shape[1], ...]
    draw_uv(flow_filename, flow)

    img_2_mapped_to_1_top = flow_warp(top_img_2, flow)
    cv2.imwrite(difference_filename, image_difference(img_2_mapped_to_1_top, g_pyramid_1[0]))


def image_difference(img1, img2):
    difference = (img1.astype(int) - img2.astype(int)) + 128
    difference = np.maximum(0, np.minimum(255, difference)).astype(np.uint8)
    return difference


def lk_hierarchy_images(input1, input2, levels):
    img1 = cv2.imread(input1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(input2, cv2.IMREAD_GRAYSCALE)
    pyramid1 = gaussPyramid(img1, levels)
    pyramid2 = gaussPyramid(img2, levels)

    u = np.zeros(pyramid1[-1].shape)
    v = np.zeros(pyramid1[-1].shape)
    w_img = pyramid2[-1]
    for level_img1, level_img2 in reversed(zip(pyramid1, pyramid2)):
        shape = level_img1.shape
        u = expand(2 * u)[:shape[0], :shape[1], ...]
        v = expand(2 * v)[:shape[0], :shape[1], ...]
        w_img = flow_warp(level_img2, (u, v))
        flow = lk_optic_flow(level_img1, w_img, 23)
        u = u + flow[0]
        v = v + flow[1]
        
    w_img = flow_warp(pyramid2[0], (u, v))
    diff_img = image_difference(w_img, img1)

    return ((u, v), diff_img)


def flow_warp(img, flow):
    x_offset = np.arange(img.shape[1]).reshape(1, img.shape[1])
    y_offset = np.arange(img.shape[0]).reshape(img.shape[0], 1)
    u_map = np.add(-flow[0] * k_flow_scale, x_offset).astype(np.float32)
    v_map = np.add(-flow[1] * k_flow_scale, y_offset).astype(np.float32)
    warped_img = cv2.remap(img, u_map, v_map, cv2.INTER_NEAREST)
    return warped_img


def write_pyramid(output_filename, pyramid):
    vertical_dims = map(lambda x: x.shape[0], pyramid)
    horizontal_dims = map(lambda x: x.shape[1], pyramid)
    vdim = max(vertical_dims)
    hdim = sum(horizontal_dims)
    output_image = np.ones((vdim, hdim)) * 255.

    start_x = 0
    for image in pyramid:
        end_x = start_x + image.shape[1]
        output_image[0:image.shape[0], start_x:end_x] = image
        start_x = end_x

    cv2.imwrite(output_filename, output_image.astype(np.uint8))


def draw_hierarchy_uv(hierarchy_images, output_filename):
    vert = []
    for (u, v), img in hierarchy_images: 
        vert.append(np.hstack((u, v)))
    image = np.vstack(vert)
    image = (normalize_image(image) * 255).astype(np.uint8)
    cv2.imwrite(output_filename, image)


def draw_hierarchy_images(hierarchy_images, output_filename):
    vert = map(lambda x: x[1], hierarchy_images)
    image = np.vstack(vert).astype(np.uint8)
    cv2.imwrite(output_filename, image)


if __name__ == '__main__':
    shift0_img = cv2.imread('input/TestSeq/Shift0.png', cv2.IMREAD_GRAYSCALE)

    analyze_optic_flow(shift0_img, 'input/TestSeq/ShiftR2.png', 'output/ps5-1-a-1.png')
    analyze_optic_flow(shift0_img, 'input/TestSeq/ShiftR5U5.png', 'output/ps5-1-a-2.png')
    analyze_optic_flow(shift0_img, 'input/TestSeq/ShiftR10.png', 'output/ps5-1-b-1.png')
    analyze_optic_flow(shift0_img, 'input/TestSeq/ShiftR20.png', 'output/ps5-1-b-2.png')
    analyze_optic_flow(shift0_img, 'input/TestSeq/ShiftR40.png', 'output/ps5-1-b-3.png')

    yos_img_1 = cv2.imread('input/DataSeq1/yos_img_01.jpg', cv2.IMREAD_GRAYSCALE)
    g_pyramid = gaussPyramid(yos_img_1, 4)
    write_pyramid('output/ps5-2-a-1.png', g_pyramid)

    l_pyramid = laplPyramid(g_pyramid)
    write_pyramid('output/ps5-2-b-1.png', l_pyramid)

    # lk_warp_test('input/TestSeq/Shift0.png', 'input/TestSeq/ShiftR2.png')
    # lk_warp_test('input/DataSeq1/yos_img_01.jpg', 'input/DataSeq1/yos_img_02.jpg')

    lk_warp_level('input/DataSeq1/yos_img_01.jpg', 'input/DataSeq1/yos_img_02.jpg', 1, 'output/ps5-3-a-1.png', 'output/ps5-3-a-2.png')
    lk_warp_level('input/DataSeq2/0.png', 'input/DataSeq2/1.png', 2, 'output/ps5-3-a-3.png', 'output/ps5-3-a-4.png')

    hierarchy_images = []
    hierarchy_images.append(lk_hierarchy_images('input/TestSeq/Shift0.png', 'input/TestSeq/ShiftR10.png', 4))
    hierarchy_images.append(lk_hierarchy_images('input/TestSeq/Shift0.png', 'input/TestSeq/ShiftR20.png', 4))
    hierarchy_images.append(lk_hierarchy_images('input/TestSeq/Shift0.png', 'input/TestSeq/ShiftR40.png', 4))

    draw_hierarchy_uv(hierarchy_images, 'output/ps5-4-a-1.png')
    draw_hierarchy_images(hierarchy_images, 'output/ps5-4-a-2.png')


    hierarchy_images = []
    hierarchy_images.append(lk_hierarchy_images('input/DataSeq1/yos_img_01.jpg', 'input/DataSeq1/yos_img_02.jpg',4))
    hierarchy_images.append(lk_hierarchy_images('input/DataSeq1/yos_img_01.jpg', 'input/DataSeq1/yos_img_03.jpg',4))

    draw_hierarchy_uv(hierarchy_images, 'output/ps5-4-b-1.png')
    draw_hierarchy_images(hierarchy_images, 'output/ps5-4-b-2.png')


    hierarchy_images = []
    hierarchy_images.append(lk_hierarchy_images('input/DataSeq2/0.png', 'input/DataSeq2/1.png',4))
    hierarchy_images.append(lk_hierarchy_images('input/DataSeq2/0.png', 'input/DataSeq2/2.png',4))

    draw_hierarchy_uv(hierarchy_images, 'output/ps5-4-c-1.png')
    draw_hierarchy_images(hierarchy_images, 'output/ps5-4-c-2.png')


    # the above results on real images are disappointing, so I decided to compare the basic flow to the
    # hierachy flow to see if the hierarchy is indeed producing better results
    img1 = cv2.imread('input/TestSeq/Shift0.png', cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread('input/TestSeq/ShiftR10.png', cv2.IMREAD_GRAYSCALE)
    flow = lk_optic_flow(img1, img2, 23)
    img_2_mapped_to_1 = flow_warp(img2, flow)
    draw_uv('output/ps5-compare-flow-basic.png', flow)
    cv2.imwrite('output/ps5-compare-warped-basic.png', image_difference(img_2_mapped_to_1, img1))
    
    hierarchy_images = []
    uv, img = lk_hierarchy_images('input/TestSeq/Shift0.png', 'input/TestSeq/ShiftR10.png', 4)
    draw_uv('output/ps5-compare-flow-hierarchy.png', uv)
    cv2.imwrite('output/ps5-compare-warped-hierarchy.png', img)


