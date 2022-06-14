import numpy as np
import cv2
import copy
from hough_circles_acc import hough_circles_acc
from hough_peaks import hough_peaks

def find_circles(BW, radius_range, original_img=None):
    # % Find circles in given radius range using Hough transform.
    # %
    # % BW: Binary (black and white) image containing edge pixels
    # % radius_range: Range of circle radii [min max] to look for, in pixels

    # % TODO: Your code here

    rIndex = 0
    radii = range(radius_range[0], radius_range[1]+1)
    H = np.zeros((BW.shape[0], BW.shape[1], len(radii)))
    for radius in radii:
        Hslice = hough_circles_acc(BW, radius)
        H[:,:,rIndex] = Hslice
        rIndex += 1

    peaks = hough_peaks(H, numpeaks=20)
    """
    for Threshold in np.arange(0.9, 0.4, -0.1):
        Hcopy = copy.deepcopy(H)
        peaks = hough_peaks(Hcopy, numpeaks=20, Threshold=Threshold * Hcopy.max())
        if original_img != None:
            image_copy = copy.deepcopy(original_img)
            map(lambda x: cv2.circle(image_copy, (x[1], x[0]), radii[x[2]], (0, 255, 0), thickness=2), peaks)
            cv2.imwrite('output/test_{}.png'.format(str(Threshold).replace('.', '_')), image_copy)
    """
   
    return map(lambda x: (x[0], x[1]), peaks), map(lambda x: radii[x[2]], peaks)
