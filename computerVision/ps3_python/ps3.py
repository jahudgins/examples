# ps2
# Jonathan Hudgins (jhudgins8@gatech.edu)
# GTID: 903050550
# CS4495 Spring 2015 OMS

import numpy as np
import numpy.linalg
import numpy.random
import cv2
import re


def read_points_file(filename):
    # read in the points into an mxn matrix
    f = open(filename, 'rt')
    lines = f.readlines()
    f.close()
    result = []
    for line in lines:
        l = map(lambda x: float(x), line.strip().split())
        result.append(np.array(l))

    return np.array(result)

def calibrate(points2d, points3d):
    """
    combine the points to create the below matrix
                                                                        m00
                                                                        m01
                                                                        m02
                                                                        m03
    Xi   Yi   Zi   1 0 0 0 0 -ui*Xi     -ui*Yi     -ui*Zi     -ui       m10
    Xi+1 Yi+1 Zi+1 1 0 0 0 0 -ui+1*Xi+1 -ui+1*Yi+1 -ui+1*Zi+1 -ui+1     m11
    ...                                                                 m12
    0 0 0 0 Xi   Yi   Zi   -vi*Xi     1 -vi*Yi     -vi*Zi     -vi       m13
    0 0 0 0 Xi+1 Yi+1 Zi+1 -vi+1*Xi+1 1 -vi+1*Yi+1 -vi+1*Zi+1 -vi+1     m20
                                                                        m21
                                                                        m22
                                                                        m23



    """
    z = np.zeros((points3d.shape[0], 4))
    ones = np.ones((points3d.shape[0], 1))
    u = points2d[:,0:1]
    v = points2d[:,1:2]
    u3 = np.multiply(u, points3d)
    v3 = np.multiply(v, points3d)
    m1 = np.hstack((points3d, ones, z, -u3, -u))
    m2 = np.hstack((z, points3d, ones, -v3, -v))
    m = np.vstack((m1, m2))

    # solve into SVD 
    U, s, V = numpy.linalg.svd(m)

    # we just use the last row: reshape into the expected matrix
    calibration = V[-1,:].reshape((3, 4))
    return calibration


def project(m, points3d):
    # create a list of 2d points projected by homogeneous matrix m
    ones = np.ones((points3d.shape[0], 1))
    projected = np.dot(m, np.hstack((points3d, ones)).T).T
    normalized = np.multiply(projected, 1/projected[:,2:3])
    points2d = normalized[:, 0:2]
    return points2d


def calc_residuals(original, projected):
    # calculate the distance from the original points to the calculated
    delta = original - projected
    squared = np.multiply(delta, delta)
    sums = np.sum(squared, axis=1)
    residuals = np.sqrt(sums)
    return residuals


def project_sampling(points2d, points3d, sample_size):
    # create camera matrix based on a limited sample size
    # compare to a test set
    combined = np.hstack((points2d, points3d))
    np.random.shuffle(combined) 
    sample_set = combined[0:sample_size,:]
    test_set = combined[sample_size:sample_size+4,:]

    # get the calibration of the sample_set
    calibration = calibrate(sample_set[:,3:5], sample_set[:,0:3])

    # use that calibration to project the test_set and compare to generate residuals
    projected = project(calibration, test_set[:,0:3])
    residuals = calc_residuals(test_set[:,3:5], projected)

    avg_residual = np.average(residuals)
    M = calibration
    
    return avg_residual, M


def calc_center(calibration_matrix):
    # center = -inv(Q) * m4
    return np.dot(-numpy.linalg.inv(calibration_matrix[:,0:3]), calibration_matrix[:,3:4])


def trials(points2d, points3d):
    # multiple trials with sample sizes of 8, 12, 16
    all_residuals = []
    residuals = []
    sample_sizes = [8, 12, 16]
    for trial in range(10):
        sample_residuals = []
        for sample_size in sample_sizes:
            avg_residual, M = project_sampling(points2d, points3d, sample_size)
            sample_residuals.append(avg_residual)
            all_residuals.append((avg_residual, M))
        residuals.append(sample_residuals)

    print "Residual averages:"
    for r, sample_size in zip(np.array(residuals).T, sample_sizes):
        print "Sample size {}".format(sample_size)
        for v in r:
            print "{}".format(v)
        print
    print

    all_residuals.sort(key=lambda x: x[0])
    print "Sample Matrix Centers:"
    for residual, M in all_residuals:
        center = calc_center(M).T
        print "residual:{}, center:{}".format(residual, center)
    print

    print "Sample Matrix:"
    for residual, M in all_residuals:
        print "residual:{}, matrix:{}".format(residual, M)
    print


def calc_fundamental_matrix(points_a_2d, points_b_2d):
    """

                                            f11
                                            f12
                                            f13
                                            f21
    u'u  u'v  u'  v'u  v'v  v'  u  v  1     f22
                                            f23
                                            f31
                                            f32
                                            f33
    """

    pFp = np.zeros((points_a_2d.shape[0],9))

    pFp[:,0] = np.multiply(points_b_2d[:,0], points_a_2d[:,0])      # u'u
    pFp[:,1] = np.multiply(points_b_2d[:,0], points_a_2d[:,1])      # u'v
    pFp[:,2] = points_b_2d[:,0]                                     # u'

    pFp[:,3] = np.multiply(points_b_2d[:,1], points_a_2d[:,0])      # v'u
    pFp[:,4] = np.multiply(points_b_2d[:,1], points_a_2d[:,1])      # v'v
    pFp[:,5] = points_b_2d[:,1]                                     # v'

    pFp[:,6] = points_a_2d[:,0]                                     # u
    pFp[:,7] = points_a_2d[:,1]                                     # v
    pFp[:,8] = 1                                                    # 1

    U, s, V = numpy.linalg.svd(pFp)
    F = V[-1,:].reshape((3, 3))
    return F


def reduce_rank(F):
    # reduce rank by setting the smallest value of the diagonal matrix from the
    # svd decomposition to 0
    U, s, V = numpy.linalg.svd(F)
    s[2] = 0
    S = np.diag(s)
    Freduced = np.dot(U, np.dot(S, V))
    return Freduced

def draw_epipolar(dst_points_2d, fundamental_reduced, input_file, output_file):
    ones = np.ones((dst_points_2d.shape[0], 1))
    dst_points_homo = np.hstack((dst_points_2d, ones))
    lines = np.dot(fundamental_reduced, dst_points_homo.T).T
    
    image = cv2.imread(input_file)
    l_line = np.cross(np.array([0, 0, 1]), np.array([0, image.shape[0], 1])) 
    r_line = np.cross(np.array([image.shape[1], 0, 1]), np.array([image.shape[1], image.shape[0], 1])) 

    for line in lines:
        l_point = np.cross(line, l_line)
        r_point = np.cross(line, r_line)
        l_2d = (l_point[0:2] / l_point[2]).astype(int)
        r_2d = (r_point[0:2] / r_point[2]).astype(int)
        cv2.line(image, (l_2d[0], l_2d[1]), (r_2d[0], r_2d[1]), (255, 0, 0))

    cv2.imwrite(output_file, image)

if __name__ == "__main__":
    a_2d = read_points_file('input/pts2d-pic_a.txt')
    a_3d = read_points_file('input/pts3d.txt')

    norm_2d = read_points_file('input/pts2d-norm-pic_a.txt')
    norm_3d = read_points_file('input/pts3d-norm.txt')

    calibration = calibrate(norm_2d, norm_3d)
    projected = project(calibration, norm_3d)
    residuals = calc_residuals(norm_2d, projected)

    print "Calibration matrix for normalized set:"
    print calibration
    print
    print "Measured normalized 2d:"
    print norm_2d
    print
    print "Calculated normalized 2d:"
    print projected
    print
    print "Residuals of normalized:"
    print residuals
    print
    print "Center:"
    print calc_center(calibration)
    print

    b_2d = read_points_file('input/pts2d-pic_b.txt')
    b_3d = read_points_file('input/pts3d.txt')

    print "** Raw **"
    trials(b_2d, b_3d)
    print

    fundamental_matrix = calc_fundamental_matrix(a_2d, b_2d)
    print "Fundamental Matrix:"
    print fundamental_matrix
    print

    fundamental_reduced = reduce_rank(fundamental_matrix)
    print "Fundamental Reduced:"
    print fundamental_reduced
    print

    draw_epipolar(b_2d, fundamental_reduced.T, 'input/pic_a.jpg', 'output/ps3-2-c-1.png')
    draw_epipolar(a_2d, fundamental_reduced, 'input/pic_b.jpg', 'output/ps3-2-c-2.png')

