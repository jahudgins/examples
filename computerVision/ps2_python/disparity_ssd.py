#
# ps2
# Jonathan Hudgins (jhudgins8@gatech.edu)
# GTID: 903050550
#
import numpy as np
import scipy.signal
import gc
import sys


def disparity_ssd(L, R):
    """Compute disparity map D(y, x) such that: L(y, x) = R(y, x + D(y, x))
    
    Params:
    L: Grayscale left image
    R: Grayscale right image, same size as L

    Returns: Disparity map, same size as L, R
    """

    # TODO: Your code here
    block_size = 13
    sum_kernel = np.ones((block_size, block_size))
    yrange = range(L.shape[0])
    last_done_ratio = 0
    max_check = R.shape[1]/3
    check_range = range(-max_check, max_check)
    # initialize to random values so that all memory gets allocated up front
    # sums_array = np.zeros((2*max_check+1, L.shape[0], L.shape[1]))
    sums_array = np.random.normal(0.0, 1.0, (len(check_range), L.shape[0], L.shape[1]))
    for xr in range(-max_check, max_check):
        xrrange = np.array(range(xr, xr + R.shape[1])) % R.shape[1]
        Rwrap =  R[np.ix_(yrange, xrrange)]
        delta = L - Rwrap
        squared = np.multiply(delta, delta)
        sum_squared = scipy.signal.convolve2d(squared, sum_kernel, 'same')
        sums_array[xr + max_check,:,:] = sum_squared

        done_ratio = (xr + max_check)/float(2 * max_check)
        if  done_ratio > 0.05 + last_done_ratio:
            sys.stdout.write('{}% '.format(int(done_ratio*100)))
            sys.stdout.flush()
            last_done_ratio = done_ratio

    sys.stdout.write('100%\n')
    min_args = np.argmin(sums_array, 0)
    # wrap for indices greater than max_check
    result = min_args - max_check

    return result
