import numpy as np
import scipy.signal
import cv2
import sys

def disparity_ncorr(L, R):
    """Compute disparity map D(y, x) such that: L(y, x) = R(y, x + D(y, x))
    
    Params:
    L: Grayscale left image
    R: Grayscale right image, same size as L

    Returns: Disparity map, same size as L, R
    """

    # TODO: Your code here
    block_size = 13
    L = L.astype(np.float32)
    R = R.astype(np.float32)
    result = np.zeros(L.shape)
    for y in range(L.shape[0]):
        yrange = np.array(range(y-block_size/2, y+block_size/2+1)) % R.shape[0]
        ix = np.ix_(yrange, range(R.shape[1]))
        image = R[ix]
        for x in range(block_size/2, L.shape[1]-block_size/2):
            xrange = np.array(range(x-block_size/2, x+block_size/2+1))
            tix = np.ix_(yrange, xrange)
            template = L[tix]
            match = cv2.matchTemplate(image.astype(np.float32), template.astype(np.float32), cv2.cv.CV_TM_CCORR_NORMED)
            result[y, x] = x - (int(np.argmax(match)) + block_size/2)

    return result

def disparity_ncorr_mine(L, R):
    block_size = 13
    sum_kernel = np.ones((block_size, block_size))
    yrange = range(L.shape[0])
    last_done_ratio = 0
    #max_check = R.shape[1] / 3
    max_check = R.shape[1] / 2
    check_range = range(-max_check, max_check)

    squaredL = np.multiply(L, L)
    sum_squaredL = scipy.signal.convolve2d(squaredL, sum_kernel, 'same')
    sum_squaredL[sum_squaredL == 0] = 1
    normalizeL = 1 / np.sqrt(sum_squaredL)

    # initialize to random values so that all memory gets allocated up front
    # sums_array = np.zeros((2*max_check+1, L.shape[0], L.shape[1]))
    correlation_array = np.zeros((len(check_range), L.shape[0], L.shape[1]))
    for xr in check_range:
        xrrange = np.array(range(xr, xr + R.shape[1])) % R.shape[1]
        ix = np.ix_(yrange, xrrange)
        Rwrap =  R[ix]
        dot = np.multiply(L, Rwrap)
        normalizeR = normalizeL[ix]

        sum_dot = scipy.signal.convolve2d(dot, sum_kernel, 'same')
        normalized_correlation = np.multiply(np.multiply(sum_dot, normalizeL), normalizeR)
        correlation_array[xr + max_check,:,:] = normalized_correlation

        done_ratio = (xr + max_check)/float(2 * max_check)
        if  done_ratio > 0.05 + last_done_ratio:
            sys.stdout.write('{}% '.format(int(done_ratio*100)))
            sys.stdout.flush()
            last_done_ratio = done_ratio

    min_args = np.argmin(correlation_array, 0)
    max_args = np.argmax(correlation_array, 0)
    # wrap for indices greater than max_check
    result = max_args - max_check

    return result
