# ps6
# Jonathan Hudgins (jhudgins8@gatech.edu)
# GTID: 903050550
# CS4495 Spring 2015 OMS

import numpy as np
import cv2
import numpy.random

import pylab

import collections
import random
import math
import sys

import os


# test
# wrap indices!
# todo: named tuple
# adjust for center point u, v
# draw particles
# draw best_patch bounds

def load_bounds(filename):
    with open(filename, 'rt') as f:
        lines = f.readlines()
    # make sure w, h are ints (which will be cast to floats) so that when added to other
    # floats we won't get rounding discrepancies
    x, y = map(lambda x: float(x), lines[0].split())
    w, h = map(lambda x: int(float(x)), lines[1].split())
    center = (x + w/2, y + h/2)
    dims = [w, h]
    return (center, dims)


def get_patch(frame_data, center, dims):
    x0 = center[0] - dims[0]/2
    y0 = center[1] - dims[1]/2
    xf = x0 + dims[0]
    yf = y0 + dims[1]
    return frame_data[1][y0:yf, x0:xf, ...]


def generate_samples(best_patch, frame_data, old_samples, dims, move_extents, num_samples, similarity_sigma, output):
    x_offsets = numpy.random.normal(0, move_extents[0], num_samples)
    y_offsets = numpy.random.normal(0, move_extents[1], num_samples)
    # x_offsets = numpy.linspace(-move_extents[0], move_extents[0], num_samples)
    # y_offsets = np.zeros(num_samples)

    new_samples = []
    current_prob = random.random()
    increment_prob = random.random() * 10 / num_samples
    old_sample_index = 0
    new_sample_index = 0

    # find min and max for the new centers
    # dims are x, y; shape is y, x
    min_center = (0 + dims[0]/2 + 3, 0 + dims[1]/2 + 3)
    max_center = (frame_data[1].shape[1] - dims[0]/2 - 3, frame_data[1].shape[0] - dims[1]/2 - 3)

    stats = []
    while new_sample_index < num_samples:
        x_offset = x_offsets[new_sample_index]
        y_offset = y_offsets[new_sample_index]
        while current_prob > 0:
            old_sample_index = (old_sample_index + 1) % len(old_samples)
            current_prob -= old_samples[old_sample_index][0]
        current_prob += increment_prob

        old_sample_probability, old_sample_center = old_samples[old_sample_index]
        new_center = (old_sample_center[0] + x_offset, old_sample_center[1] + y_offset)

        # ensure that new_bounds are valid
        while new_center[0] < min_center[0] or new_center[1] < min_center[1] or new_center[0] > max_center[0] or new_center[1] > max_center[1]:
            x_offset = numpy.random.normal(0, move_extents[0], 1)[0]
            y_offset = numpy.random.normal(0, move_extents[1], 1)[0]
            new_center = (old_sample_center[0] + x_offset, old_sample_center[1] + y_offset)

        new_patch = get_patch(frame_data, new_center, dims)
        similar_probability, mse = calculate_similar_probability(best_patch, new_patch, similarity_sigma)
        stats.append((similar_probability, mse))
        new_probablility = old_sample_probability * similar_probability
        new_samples.append((new_probablility, new_center))

        new_sample_index += 1

    """
    total = sum(map(lambda x: x[0], stats))
    for stat in stats:
        print stat[0]/total, stat[1]
    """

    # normalize probabilities
    total_prob = sum(map(lambda x: x[0], new_samples))
    new_samples = map(lambda x: (x[0]/total_prob, x[1]), new_samples)

    """
    if output:
        sorted_samples = map(lambda x: x[0], new_samples)
        sorted_samples.sort()
        sys.stdout.write("\n")
        for perc in [2, 5, 10]:
            count = len(sorted_samples) * perc / 100
            sys.stdout.write("{}%:{:0.4}, ".format(perc, sum(sorted_samples[-count:])))
        sys.stdout.write("\n")
    """
        
    return new_samples


def calculate_similar_probability(patch0, patch1, sigma):
    delta = patch0 - patch1
    mse = float(np.multiply(delta, delta).sum())
    for dim in patch0.shape:
        mse /= dim
    return math.exp(- mse / (2 * sigma * sigma)), mse


def weighted_mean(samples):
    center = [0, 0]
    for sample in samples:
        center[0] += sample[0] * sample[1][0]
        center[1] += sample[0] * sample[1][1]
    return center


def draw_samples(src_img, samples, dims):
    for sample in samples:
        cv2.circle(src_img, (int(sample[1][0]), int(sample[1][1])), 1, (0, 0, 255))

    center = weighted_mean(samples)

    start = (int(center[0] - dims[0]/2), int(center[1] - dims[1]/2))
    end = (int(center[0] + dims[0]/2), int(center[1] + dims[1]/2))
    cv2.rectangle(src_img, start, end, (0, 0, 255), 2)

    return src_img


def track_face(bounds_filename, video_filename, similarity_sigma=2.0, extent_scale=0.2, num_samples=40,
                window_scale=1.0, capture_frames=None, alpha_best=0.0):
    center, dims = load_bounds(bounds_filename)
    return track_face_bounds((center, dims), video_filename, similarity_sigma, extent_scale, num_samples, window_scale, capture_frames, alpha_best)

def track_face_bounds((center, dims), video_filename, similarity_sigma=2.0, extent_scale=0.2, num_samples=40,
                window_scale=1.0, capture_frames=None, alpha_best=0.0):
    capture = cv2.VideoCapture()
    capture.open(video_filename)
    isOpened = capture.isOpened()
    width = capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    height = capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    msec = capture.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
    num_frames = capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    frame_data = capture.read()

    move_extents = (dims[0] * extent_scale, dims[1] * extent_scale)
    dims[0] = int(dims[0] * window_scale)
    dims[1] = int(dims[1] * window_scale)
    start_patch = get_patch(frame_data, center, dims)
    best_patch = np.copy(start_patch)

    samples = [(1.0, center)]
    
    output_frames = []
    if capture_frames == None:
        capture_frames = [int(num_frames)]
    num_frames = max(capture_frames)
    for iteration in range(num_frames):
        if iteration % max(1, (num_frames/10)) == 0:
            print "{}% ".format(iteration * 100 / num_frames),
        frame_data = capture.read()
        samples = generate_samples(best_patch, frame_data, samples, dims, move_extents, num_samples=num_samples, similarity_sigma=similarity_sigma, output=((iteration+1) in capture_frames))

        
        weighted_patch = get_patch(frame_data, weighted_mean(samples), dims)
        best_patch = alpha_best * weighted_patch + (1 - alpha_best) * best_patch

        if (iteration+1) in capture_frames:
            output_frames.append(draw_samples(frame_data[1], samples, dims))

        """
        probabilities = map(lambda x: x[0], samples)
        bins = np.linspace(min(probabilities), max(probabilities), 10)
        n, bins, patches = pylab.hist(probabilities, bins, normed=1, histtype='bar', rwidth=0.8)
        pylab.show()
        """
    print "100%"

    return start_patch, output_frames


if __name__ == "__main__":
    # random.seed(1)
    # numpy.random.seed(1)

    files = ['input/pres_debate.txt', 'input/pres_debate.avi']
    capture_frames = [28, 84, 144]
    start_patch, output_frames = track_face(*files, capture_frames=capture_frames)
    cv2.imwrite('output/ps6-1-a-1.png', start_patch)
    cv2.imwrite('output/ps6-1-a-2.png', output_frames[0])
    cv2.imwrite('output/ps6-1-a-3.png', output_frames[1])
    cv2.imwrite('output/ps6-1-a-4.png', output_frames[2])
   
    
    print "analyzing window_scale"
    for inv_window_scale in [2, 4, 8, 16, 32]:
        start_patch, output_frames = track_face(*files, window_scale=1.0/inv_window_scale, capture_frames=capture_frames)
        for frame, img in zip(capture_frames, output_frames):
            cv2.imwrite('window_scale/{:03}_img_{:02}.png'.format(frame, inv_window_scale), img)

    print "analyzing similarity_sigma"
    for similarity_sigma in [1, 2, 4, 8, 16]:
        start_patch, output_frames = track_face(*files, similarity_sigma=similarity_sigma, capture_frames=capture_frames)
        for frame, img in zip(capture_frames, output_frames):
            cv2.imwrite('similarity_sigma/{:03}_img_{:02}.png'.format(frame, similarity_sigma), img)

    print "analyzing num_samples"
    for num_samples in [10, 40, 160, 640]:
        start_patch, output_frames = track_face(*files, num_samples=num_samples, capture_frames=capture_frames)
        for frame, img in zip(capture_frames, output_frames):
            cv2.imwrite('num_samples/{:03}_img_{:03}.png'.format(frame, num_samples), img)

    # history of experiment
    #  starting values:
    #   extent_scale=0.2
    #   num_samples=40
    #   window_scale=1.0
    #
    #  experiment with similarity_sigma in [1, 2, 4, 8, 16]
    #   similarity_sigma = 4 best
    #  experiment with extent_scale in [0.1, 0.2, 0.3]
    #   extent_scale = 0.2 best
    #  experiment with num_samples in [10, 20 40, 80, 160]
    #   num_samples = 40 best
    #  experiment with window_scale in [1.0, 0.5, 0.25, 0.125]
    #   window_scale = 1

    files = ['input/noisy_debate.txt', 'input/noisy_debate.avi']
    capture_frames = [14, 32, 46]

    similarity_sigma=4.0
    extent_scale=0.2
    num_samples=40
    window_scale=1.0

    start_patch, output_frames = track_face(
            *files,
            similarity_sigma=similarity_sigma,
            extent_scale=extent_scale,
            num_samples=num_samples,
            window_scale=window_scale,
            capture_frames=capture_frames)
    cv2.imwrite('output/ps6-1-e-1.png', output_frames[0])
    cv2.imwrite('output/ps6-1-e-2.png', output_frames[1])
    cv2.imwrite('output/ps6-1-e-3.png', output_frames[2])

    capture_frames = [15, 50, 140]
    bounds = ([580, 435], [60, 90])

    """
    alpha_best = 0.375
    similarity_sigma=4.0
    extent_scale=0.2
    num_samples=150
    window_scale=1.0

    for alpha_best in [0.101, 0.201, 0.301, 0.361, 0.375, 0.401, 0.501, 0.601, 0.701]:
        start_patch, output_frames = track_face_bounds(
                bounds,
                'input/noisy_debate.avi',
                similarity_sigma=similarity_sigma,
                extent_scale=extent_scale,
                num_samples=num_samples,
                window_scale=window_scale,
                capture_frames=capture_frames,
                alpha_best=alpha_best)

        for frame, img in zip(capture_frames, output_frames):
            directory = 'alpha_best/{:03}'.format(frame)
            if not os.path.isdir(directory):
                os.makedirs(directory)
            cv2.imwrite('{}/img_{:03}.png'.format(directory, alpha_best), img)

    sys.exit(0)
    """

    alpha_best = 0.375
    similarity_sigma=4.0
    extent_scale=0.2
    num_samples=150
    window_scale=1.0

    start_patch, output_frames = track_face_bounds(
            bounds,
            'input/pres_debate.avi',
            similarity_sigma=similarity_sigma,
            extent_scale=extent_scale,
            num_samples=num_samples,
            window_scale=window_scale,
            capture_frames=capture_frames,
            alpha_best=alpha_best)


    cv2.imwrite('output/ps6-2-a-1.png', start_patch)
    cv2.imwrite('output/ps6-2-a-2.png', output_frames[0])
    cv2.imwrite('output/ps6-2-a-3.png', output_frames[1])
    cv2.imwrite('output/ps6-2-a-4.png', output_frames[2])

    alpha_best = 0.1
    similarity_sigma=4.0
    extent_scale=0.2
    num_samples=150
    window_scale=1.0

    start_patch, output_frames = track_face_bounds(
            bounds,
            'input/noisy_debate.avi',
            similarity_sigma=similarity_sigma,
            extent_scale=extent_scale,
            num_samples=num_samples,
            window_scale=window_scale,
            capture_frames=capture_frames,
            alpha_best=alpha_best)

    cv2.imwrite('output/ps6-2-b-1.png', start_patch)
    cv2.imwrite('output/ps6-2-b-2.png', output_frames[0])
    cv2.imwrite('output/ps6-2-b-3.png', output_frames[1])
    cv2.imwrite('output/ps6-2-b-4.png', output_frames[2])

