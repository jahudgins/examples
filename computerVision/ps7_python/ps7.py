# ps7
# Jonathan Hudgins (jhudgins8@gatech.edu)
# GTID: 903050550
# CS4495 Spring 2015 OMS

import numpy as np
import cv2
import numpy.random

import collections
import random
import math
import sys
import json
import os
import cPickle

def calculate_binary_image(image, last_image, theta):
    output = np.zeros((image.shape[0], image.shape[1]))
    abs_delta = np.abs(image - last_image).max(axis=2)
    output[abs_delta >= theta] = 1
    return output


def calculate_MHI(filename, end, theta, sigma):
    capture = cv2.VideoCapture()
    capture.open(filename)
    tau = end
    last_image = cv2.GaussianBlur(capture.read()[1].astype(np.float), (0,0), sigma)
    MHI = np.zeros((last_image.shape[0:2]))
    for t in range(tau):
        image = cv2.GaussianBlur(capture.read()[1].astype(np.float), (0,0), sigma)
        binary_image = calculate_binary_image(image, last_image, theta)
        MHI[binary_image == 1] = tau
        MHI[binary_image == 0] -= 1
        MHI = np.maximum(MHI, 0)
        last_image = image

    return MHI / tau


def moment(image, i, j):
    y_arr = np.arange(image.shape[0]).reshape((image.shape[0], 1)).astype(np.float64)
    x_arr = np.arange(image.shape[1]).reshape((1, image.shape[1])).astype(np.float64)
    y_pow = np.power(y_arr, j)
    x_pow = np.power(x_arr, i)
    y_mult = np.multiply(y_pow, np.ones(image.shape))
    x_mult = np.multiply(x_pow, np.ones(image.shape))
    return np.multiply(x_mult, np.multiply(y_mult, image)).sum()


def calc_central_moment(image, i, j, x_mean, y_mean):
    y_arr = np.arange(image.shape[0]).reshape((image.shape[0], 1)).astype(np.float64)
    x_arr = np.arange(image.shape[1]).reshape((1, image.shape[1])).astype(np.float64)
    y_pow = np.power(y_arr - y_mean, j)
    x_pow = np.power(x_arr - x_mean, i)
    y_mult = np.multiply(y_pow, np.ones(image.shape))
    x_mult = np.multiply(x_pow, np.ones(image.shape))
    return np.multiply(x_mult, np.multiply(y_mult, image)).sum()


def calc_image_moments(image, moment_index_pairs):
    mean_divisor = moment(image, 0, 0)
    x_mean = moment(image, 1, 0) / mean_divisor
    y_mean = moment(image, 0, 1) / mean_divisor

    central_moment00 = calc_central_moment(image, 0, 0, x_mean, y_mean)

    central_moments = []
    scale_invariant_moments = []
    for p, q in moment_index_pairs:
        central_moment = calc_central_moment(image, p, q, x_mean, y_mean)
        central_moments.append(central_moment)
        scale_invariant_moments.append(central_moment / math.pow(central_moment00, 1 + (p+q)/2.))

    return [central_moments, scale_invariant_moments]


def calculate_signature(filename, end, theta, sigma, moment_index_pairs):
    MHI = calculate_MHI(filename, end, theta, sigma)
    MEI = np.zeros(MHI.shape)
    MEI[MHI > 0] = 1
    MHI_central_moments, MHI_scale_invariant_moments = calc_image_moments(MHI, moment_index_pairs)
    MEI_central_moments, MEI_scale_invariant_moments = calc_image_moments(MEI, moment_index_pairs)
    return (np.array(MHI_central_moments + MEI_central_moments),
            np.array(MHI_scale_invariant_moments + MEI_scale_invariant_moments))


def normalize_signatures(image_signatures):
    signatures_matrices = []
    for scale_type_index, scale_type in enumerate(['basic', 'invariant']):
        signatures_matrix = np.array(map(lambda x: x[1][scale_type_index], image_signatures))
        signatures_matrix -= signatures_matrix.min(axis=0)
        signatures_matrix /= signatures_matrix.max(axis=0)
        signatures_matrices.append(signatures_matrix)

    indices = map(lambda x: x[0], image_signatures)
    return zip(indices, list(signatures_matrices[0]), list(signatures_matrices[1]))


def find_nearest_neighbor(image_signature, training_data, signature_index):
    best_training = training_data[0]
    signature = image_signature[1][signature_index]
    best_distance = np.linalg.norm(best_training[1][signature_index] - signature)
    for training in training_data:
        training_signature = training[1][signature_index]
        distance = np.linalg.norm(training_signature - signature)
        if distance < best_distance:
            best_distance = distance
            best_training = training

    return best_training[0]


def analyze_signatures(image_signatures):
    for signature_type in ['Standard', 'Normalized']:
        basic_confusion_matrix = np.zeros((3, 3))
        scale_invarient_confusion_matrix = np.zeros((3, 3))
        person_confusion_matrix = np.zeros((3, 3, 3))
        
        for image_signature_index, image_signature in enumerate(image_signatures):
            training_data = image_signatures[:image_signature_index] + image_signatures[image_signature_index+1:]
            true_action = image_signature[0][0]

            (calculated_action, person, take) = find_nearest_neighbor(image_signature, training_data, 0)
            basic_confusion_matrix[calculated_action-1, true_action-1] += 1

            (calculated_action, person, take) = find_nearest_neighbor(image_signature, training_data, 1)
            scale_invarient_confusion_matrix[calculated_action-1, true_action-1] += 1

            person = image_signature[0][1]
            training_data_without_person = filter(lambda x: x[0][1] != person, image_signatures)
            (calculated_action, calculated_person, take) = find_nearest_neighbor(image_signatures[image_signature_index], training_data_without_person, 1)
            person_confusion_matrix[person-1][calculated_action-1, true_action-1] += 1
            

        average_person_confusion_matrix = person_confusion_matrix.sum(axis=0) / 3.0

        print "{} Basic Confusion Matrix:\n{}\n".format(signature_type, basic_confusion_matrix)
        print "{} Scale Invarient Confusion Matrix:\n{}\n".format(signature_type, scale_invarient_confusion_matrix)
        print "{} Person 1 Confusion Matrix:\n{}\n".format(signature_type, person_confusion_matrix[0])
        print "{} Person 2 Confusion Matrix:\n{}\n".format(signature_type, person_confusion_matrix[1])
        print "{} Person 3 Confusion Matrix:\n{}\n".format(signature_type, person_confusion_matrix[2])
        print "{} Person Average Confusion Matrix:\n{}\n".format(signature_type, average_person_confusion_matrix)
        print
        print

        image_signatures = normalize_signatures(image_signatures)


if __name__ == "__main__":

    """
    # for quicker iteration on the analysis
    with open('image_signatures.p', 'rb') as pickle_file:
        image_signatures = cPickle.load(pickle_file)

    analyze_signatures(image_signatures)
    sys.exit(0)
    """

    capture = cv2.VideoCapture()
    capture.open('input/PS7A1P1T1.avi')
    isOpened = capture.isOpened()
    width = capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    height = capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    msec = capture.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
    num_frames = capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)

    frame = 0
    binary_output_frames = [10, 20, 30]
    binary_output_files = ['output/ps7-1-a-1.png', 'output/ps7-1-a-2.png', 'output/ps7-1-a-3.png']
    
    # tried range of theta's from 1 to 100
    # tried range of sigma's from 2.0 to 5.0
    # the combination that seems to best capture the motion was theta=30, sigma=2.5
    theta = 24
    sigma = 2.4
    last_image = cv2.GaussianBlur(capture.read()[1].astype(np.float), (0,0), sigma)
    for t in range(max(binary_output_frames)):
        frame += 1
        frame_data = capture.read()
        image = cv2.GaussianBlur(capture.read()[1].astype(np.float), (0,0), sigma)
        if frame == binary_output_frames[0]:
            binary_output_frames.pop(0)
            output_file = binary_output_files.pop(0)
            binary_image = calculate_binary_image(image, last_image, theta)
            cv2.imwrite(output_file, binary_image.astype(np.uint8) * 255)
            # cv2.imwrite(output_file + "{:03}-{:0.3}.png".format(theta, sigma), binary_image.astype(np.uint8) * 255)
        last_image = image


    action_person_take_end = [(1, 2, 2, 30), (2, 2, 2, 50), (3, 2, 2, 30)]
    output_filenames = ['output/ps7-1-b-1.png', 'output/ps7-1-b-2.png', 'output/ps7-1-b-3.png']

    theta = 24
    sigma = 2.4
    for action, person, take, end in action_person_take_end:
        print "processing action:{}, person:{}, take:{}".format(action, person, take)
        MHI = calculate_MHI('input/PS7A{}P{}T{}.avi'.format(action, person, take), end, theta, sigma)
        output_filename = output_filenames.pop(0)
        cv2.imwrite(output_filename, (MHI * 255).astype(np.uint8))


    action_person_take_end = [  ((1, 1, 1), 60), ((1, 1, 2), 50), ((1, 1, 3), 50),
                                ((1, 2, 1), 30), ((1, 2, 2), 30), ((1, 2, 3), 30),
                                ((1, 3, 1), 40), ((1, 3, 2), 40), ((1, 3, 3), 40),
                                ((2, 1, 1), 50), ((2, 1, 2), 60), ((2, 1, 3), 60),
                                ((2, 2, 1), 50), ((2, 2, 2), 50), ((2, 2, 3), 60),
                                ((2, 3, 1), 50), ((2, 3, 2), 50), ((2, 3, 3), 50),
                                ((3, 1, 1), 40), ((3, 1, 2), 30), ((3, 1, 3), 30),
                                ((3, 2, 1), 20), ((3, 2, 2), 30), ((3, 2, 3), 30),
                                ((3, 3, 1), 20), ((3, 3, 2), 30), ((3, 3, 3), 30)]

    theta = 24
    sigma = 2.4
    image_signatures = []
    moment_index_pairs = [[2, 0], [0, 2], [1, 2], [2, 1], [2, 2], [3, 0], [0, 3]]
    for (action, person, take), end in action_person_take_end:
        filename = 'input/PS7A{}P{}T{}.avi'.format(action, person, take)
        image_signature = calculate_signature(filename, end, theta, sigma, moment_index_pairs)
        image_signatures.append(((action, person, take), image_signature))

    with open('image_signatures.p', 'wb') as pickle_file:
        cPickle.dump(image_signatures, pickle_file)

    analyze_signatures(image_signatures)

