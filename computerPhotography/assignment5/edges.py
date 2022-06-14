# ASSIGNMENT 5
# Jonathan Hudgins (jhudgins8)
# GTID: 903050550
# edge detection

import cv2
import numpy as np
import scipy.signal
import scipy.ndimage

def gaussian(sigma, size):
    m = np.zeros((size, size))
    m[size/2, size/2] = 1
    return scipy.ndimage.gaussian_filter(m, sigma)

if __name__ == '__main__':
    source = cv2.imread('test_image.jpg', cv2.IMREAD_GRAYSCALE)
    kernels = [
            np.matrix([ [0, -1, 0],
                        [-1, 2, 0],
                        [0, 0, 0]]),

            np.matrix([ [-1, -1, 0],
                        [-1,  3, 0],
                        [0, 0, 0]]),

            np.matrix([ [-1, -2, 0],
                        [-2, 5, 0],
                        [0, 0, 0]]),
            ]

    gaussian_settings = [   (1, 3),
                    (.5, 3),
                    (2, 3),
                    (1, 5),
                    (2, 5),
                    (.5, 5),
                    (1, 7), 
                    (.5, 7), 
                    (2, 7),
                ]

    thresholds = [.04, .05, .07, .1]
    """
    for threshold in thresholds:
        for idx, kernel in enumerate(kernels):
            for gaussian_setting in gaussian_settings:
    """
    for threshold in [0.05]:
        for idx, kernel in enumerate(kernels):
            for gaussian_setting in [(1, 7)]:
                g = gaussian(*gaussian_setting)
                smooth_edge_kernel = scipy.signal.convolve2d(g, kernel, mode='same', boundary='wrap')
                gradient = scipy.signal.convolve2d(source, smooth_edge_kernel, mode='same', boundary='wrap')
                gradient_from_median = np.absolute(gradient - np.median(gradient))
                gradient_normalized = gradient_from_median / gradient_from_median.max()
                # cv2.imwrite('gradient-k{}-g{}-{}.png'.format(idx, gaussian_setting[0], gaussian_setting[1]), (gradient_normalized * 255).astype(np.uint8))

                edges = np.maximum(np.minimum((gradient_normalized - threshold) * 255 * 255, 255), 0)
                cv2.imwrite('edges-k{}-g{}-{}-t{}.png'.format(idx, gaussian_setting[0], gaussian_setting[1], threshold), edges)

    img_smoothed = cv2.GaussianBlur(source, (7, 7), 1)
    img_smoothed_edges = cv2.Canny(img_smoothed, 15, 45, L2gradient=True)
    cv2.imwrite('canny.png', img_smoothed_edges)


    # threshold=0.05, kernels[1], gaussian 1, 7
