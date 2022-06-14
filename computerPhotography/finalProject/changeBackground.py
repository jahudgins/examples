# Final project
# Computer Photography
# Jonathan Hudgins (jhudgins8)
# GTID: 903050550


import cv2
import numpy as np
import numpy.linalg
import scipy.signal

import os
import argparse
import time
import math
import sys

import assignment6
import assignment6_test

# from sklearn.neural_network import BernoulliRBM
from sklearn.cluster import KMeans


def make_colors(num_colors):
    colors = np.zeros((num_colors, 3))
    step = int(255 / math.pow(num_colors, 1/3.))
    color_index = 0
    for r in range(0, 255, step):
        for g in range(0, 255, step):
            for b in range(0, 255, step):
                colors[color_index] = np.array((r, g, b))
                color_index += 1
                if color_index == num_colors:
                    return colors
    return colors


def convolve3d(image, kernel):
    if len(image.shape) == 2:
        convolved = scipy.signal.convolve2d(image, kernel, 'same')
    else:
        convolved = np.zeros(image.shape)
        for color_idx in range(3):
            convolved[:,:,color_idx] = scipy.signal.convolve2d(image[:,:,color_idx], kernel, 'same')
    return convolved


def generate_attributes(image):
    gaussian_kernel = np.array([0.05, 0.25, 0.4, 0.25, 0.05])
    delta_gaussian_kernel = gaussian_kernel + np.array([0.2, 0.2, -0.8, 0.2, 0.2])
    inverted_gaussian_kernel = 1 / gaussian_kernel
    inverted_gaussian_kernel /=  inverted_gaussian_kernel.sum()

    attribute_images = [image[:,:,0], image[:,:,1], image[:,:,2]]
    for kernel_index, kernel in enumerate([gaussian_kernel, delta_gaussian_kernel, inverted_gaussian_kernel]):
        kernel = np.outer(kernel, kernel)
        attribute_image = convolve3d(image, kernel)
        cv2.imwrite('analysis/filtered_{}.png'.format(kernel_index), attribute_image)
        for dim in range(attribute_image.shape[2]):
            attribute_images.append(attribute_image[:,:,dim])

    y_coord = np.multiply(np.ones(image.shape[0:2]), np.arange(image.shape[0]).reshape((image.shape[0], 1)))
    x_coord = np.multiply(np.ones(image.shape[0:2]), np.arange(image.shape[1]).reshape((1, image.shape[1])))

    attribute_images.append(y_coord)
    attribute_images.append(x_coord)

    return attribute_images


def make_clusters(attributes, num_clusters=40):
    data = np.zeros(attributes[0].shape + (len(attributes),))
    for attribute_index, attribute in enumerate(attributes):
        normalized_attribute = attribute.astype(float) - attribute.min()
        normalized_attribute = normalized_attribute / normalized_attribute.max()
        data[:,:,attribute_index] = normalized_attribute
    data = data.reshape((data.shape[0] * data.shape[1], data.shape[2]))

    start = time.time()
    kmeans = KMeans(init='k-means++', n_clusters=num_clusters, n_init=10, n_jobs=-2)
    kmeans.fit(data)
    end = time.time()
    print "{}s".format(end - start)
    return kmeans.labels_.reshape(attributes[0].shape)


def separate_objects(source, t1, t2, aperture, sigma):
    print t1, t2, aperture, sigma
    img_smoothed = cv2.GaussianBlur(source, (0, 0), sigma)
    return cv2.Canny(img_smoothed, threshold1=15, threshold2=45, apertureSize=aperture, L2gradient=True)


def similar_select(image, background, starting, color_threshold):
    queue = starting
    queued_set = set(starting)
    count = 0
    while len(queue) > 0:
        point = queue.pop(0)
        background[point] = 1
        color = image[point]
        iystart = max(0, point[0] - 1)
        iyend = min(image.shape[0], point[0] + 2)
        ixstart = max(0, point[1] - 1)
        ixend = min(image.shape[1], point[1] + 2)
        count += 1
        if count % 100 == 0:
            print "queue-len:{}, iystart:{}, ixstart:{}, num_back:{}".format(len(queue), iystart, ixstart, len(background[background != 0]))

        for iy in range(iystart, iyend):
            for ix in range(ixstart, ixend):
                next_point = (iy, ix)
                if next_point == point:
                    continue
                if background[next_point]!=0:
                    continue
                if next_point in queued_set:
                    continue
                next_color = image[next_point]
                if numpy.linalg.norm(color - next_color) < color_threshold:
                    queue.append(next_point)
                    queued_set.add(next_point)

"""
>>> X = np.array([[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 1]])
>>> model = BernoulliRBM(n_components=2)
>>> model.fit(X)
"""
def draw_crop(img_source, x_start, x_end, y_start, y_shelf):
    img_show_crop = np.zeros(img_source.shape)

    img_show_crop[y_start:,x_start:x_end] = img_source[y_start:,x_start:x_end]
    img_show_crop[y_shelf:,:] = img_source[y_shelf:,:]
    cv2.imwrite('analysis/crop.png', img_show_crop)


def clusters_to_background(outprefix, clusters_list, x_start, x_end, y_start, y_shelf):
    for clusters_index, clusters in enumerate(clusters_list):
        background = np.zeros(clusters.shape)
        background_values = clusters[0:y_start,:].flatten()
        background_values = np.hstack((background_values, clusters[:y_shelf,0:x_start].flatten()))
        background_values = np.hstack((background_values, clusters[:y_shelf,x_end:].flatten()))
        background_values = set(background_values.tolist())
        for background_value in background_values:
            background[clusters == background_value] = 1

        cv2.imwrite('analysis/{}background_{}.png'.format(outprefix, clusters_index), background.astype(np.uint8)*255)


def edge_analysis(img_source):
    for t1 in [10, 15, 20]:
        for t2 in [30, 45, 80]:
            for aperture in [3, 5, 7]:
                for sigma in [2, 3, 5]:
                    img_objects = separate_objects(img_source, t1, t2, aperture, sigma)
                    name = 'objects_t{}-{}_a{}-s{}'.format(t1, t2, aperture, sigma)
                    cv2.imwrite(os.path.join('analysis', name + source_file), img_objects)
                    # cv2.imwrite(os.path.join('analysis', 'objects_' + source_file), img_objects)


def gauss_similar_select(img_source):
    gauss_source = assignment6.gaussPyramid(img_source, 5)
    gauss_background = []

    for level, img_level in enumerate(gauss_source):
        cv2.imwrite("analysis/gauss-{}.png".format(level), img_level.astype(np.uint8))
        background = np.zeros(img_level.shape[0:2])

        queue = []
        for y in range(int(img_level.shape[0] * 0.15)):
            for x in range(img_level.shape[1]):
                queue.append((y, x))

        for y in range(int(img_level.shape[0] * 0.15), int(img_level.shape[0] * 0.65)):
            for x in range(int(img_level.shape[1] * 0.15)):
                queue.append((y, x))

        for y in range(int(img_level.shape[0] * 0.15), int(img_level.shape[0] * 0.65)):
            for x in range(img_level.shape[1] - int(img_level.shape[1] * 0.15), img_level.shape[1]):
                queue.append((y, x))

        similar_select(img_level, background, queue, 7.5)

        cv2.imwrite("analysis/background-{}.png".format(level), (background * 255).astype(np.uint8))
        gauss_background.append(img_level)


def write_clusters(output_prefix, clusters_list):
    for clusters_index, clusters in enumerate(clusters_list):
        colors = make_colors(clusters.max() + 1)
        materials = colors[clusters]
        cv2.imwrite('analysis/{}{}.png'.format(output_prefix, clusters_index), materials)


def load_clusters(output_prefix):
    clusters_list = []
    while True:
        filename = 'analysis/{}{}.png'.format(output_prefix, len(clusters_list))
        if not os.path.isfile(filename):
            return clusters_list

        materials = cv2.imread(filename)
        all_colors = materials.reshape((materials.shape[0] * materials.shape[1], materials.shape[2]))
        list_of_color_arrays = map(tuple, all_colors)
        colors = np.array(list(set(list_of_color_arrays)))
        clusters = np.zeros(materials.shape[0:2])
        for color_index, color in enumerate(colors):
            clusters[np.all(materials == color, axis=2)] = color_index
        clusters_list.append(clusters)


def initial_clustering(output_prefix, img_source, x_start, x_end, y_start, y_shelf):
    attributes = generate_attributes(img_source)

    clusters_list = []
    clusters_list.append(make_clusters(attributes))             # 0: all attributes
    clusters_list.append(make_clusters(attributes[0:3]))        # 1: just original color
    clusters_list.append(make_clusters(attributes[3:6]))        # 2: just blurred image
    clusters_list.append(make_clusters(attributes[0:6]))        # 3: original color and blurred image
    clusters_list.append(make_clusters(attributes[0:6] + attributes[-2:]))  # 4: original, blurred, and position
    clusters_list.append(make_clusters(attributes[3:-2]))       # 5: blurred, delta_gaussian, inverse_gaussian

    write_clusters(output_prefix, clusters_list)
    clusters_to_background(output_prefix, clusters_list, x_start, x_end, y_start, y_shelf)
 

def second_clustering(output_prefix, img_source, x_start, x_end, y_start, y_shelf):
    attributes = generate_attributes(img_source)

    # 0, 4, and 5 from above
    # enhance position (which seems to distinguish a bit better) and increase number of clusters
    attributes[-2] = attributes[-2] * 2
    attributes[-1] = attributes[-1] * 2
    clusters_list = []
    clusters_list.append(make_clusters(attributes, num_clusters=60))
    clusters_list.append(make_clusters(attributes[0:6] + attributes[-2:], num_clusters=60))
    clusters_list.append(make_clusters(attributes[3:-2], num_clusters=60))

    write_clusters(output_prefix, clusters_list)
    clusters_to_background(output_prefix, clusters_list, x_start, x_end, y_start, y_shelf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Change the background to the specified color")
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    source_file = os.path.basename(args.source)
    img_source = cv2.imread(args.source)

    y_start = int(img_source.shape[0] * 0.19)
    y_shelf = int(img_source.shape[0] * 0.72)
    x_start = int(img_source.shape[1] * 0.17)
    x_end = int(img_source.shape[1] * 0.85)

    initial_outputprefix = 'materials_'
    second_outputprefix = 'materials2_'

    """
    draw_crop(img_source, x_start, x_end, y_start, y_shelf)

    edge_analysis(img_source)

    gauss_similar_select(img_source)


    initial_clustering(initial_outputprefix, img_source, x_start, x_end, y_start, y_shelf)
    second_clustering(second_outputprefix, img_source, x_start, x_end, y_start, y_shelf)

    clusters_list = load_clusters(initial_outputprefix)
    clusters_to_background(initial_outputprefix, clusters_list, x_start, x_end, y_start, y_shelf)
    """

    # combine masks so that foreground from any of the three images is foreground
    background_mask = cv2.imread('analysis/materials_background_0.png') / 255
    background_mask[cv2.imread('analysis/materials_background_4.png') == 0] = 0
    background_mask[cv2.imread('analysis/materials_background_5.png') == 0] = 0
    cv2.imwrite('analysis/combined_mask.png', background_mask.astype(np.uint8) * 255)

    background = cv2.imread('plain_background.jpg')
    background = cv2.resize(background, (img_source.shape[1], img_source.shape[0]), interpolation=cv2.INTER_LANCZOS4)
    # https://www.flickr.com/photos/rubyblossom/6377796681/in/photolist-7NDX9P--7yPhGw-aHzSKK-a2iHsa-8HmjkU-47bdQV-7xjMyr-6sMGTE-bq39eW-auag7Z-7W9tup-aMbz1z-8Rq2vT-bvxJWi-dmdUYJ-7wEDmf-76QocF-91QmTe-6zpVPq-9jnteE-8JVZxJ-8j6JHY-a369qE-6saqEp-6wgEfx-ayEDcu-dfmTRk-8HirFv-bzprtF-6GjSwv-4ugfBG-dfmVbY-cs36p9-dme1Yo-9MYWgi-8X6otJ-2H2bWk-5mPFL1-8SZ1dZ-7Zzyq5-6wfL9z-aah5G3-8rWpLp-8pZi9e-9AaAai-3cS1g8-7YcPtP-bvmuj4-7mdbqA
    # rubyblossom.

    # http://upload.wikimedia.org/wikipedia/commons/a/aa/Taj_Mahal_East_Side.JPG

    out_layers = []
    for ch in range(3):
        lp_black, lp_white, gp_black, gp_white, gp_mask, out_pyr, out_img = \
                assignment6_test.run_blend(img_source[:,:,ch], background[:,:,ch], background_mask[:,:,ch])
        out_layers.append(out_img)
    out_img = cv2.merge(out_layers)
    cv2.imwrite('output/mat_background_combined_pyramid.png', out_img)

    """
    new_image = np.zeros(img_source.shape)
    new_image[background_mask == 0] = img_source[background_mask == 0]
    new_image[background_mask == 1] = background[background_mask == 1]
    cv2.imwrite('output/background_replaced.png', new_image)
    """

