import numpy as np
 
from hough_lines_draw import hough_peak_to_line

def hough_peaks(H, numpeaks=1, Threshold=None, NHoodSize=None):
    flat = H.flatten()

    if Threshold is None:
        Threshold = 0.5 * flat.max()
    if NHoodSize is None:
        NHoodSize = np.maximum(((np.array(H.shape) + 49) / 100.).astype(int) * 2 + 1, 3)
    
    # TODO: Compute peaks: Qx2 array with row, col indices of peaks
    indices = flat.argsort().tolist()
    indices.reverse()

    # increment until threshold
    threshold_index = 0
    while flat[indices[threshold_index]] > Threshold:
        threshold_index += 1
    indices_threshold = indices[:threshold_index]

    peaks = list()

    # remove indices that are within the NHoodSize
    for index in indices_threshold:
        indexMat = np.unravel_index(index, H.shape)

        # if we have already zeroed out this entry, skip it
        value = H[indexMat]
        if value == 0:
            continue

        # zero out everything in the range of NHoodSize
        start = np.maximum(0, indexMat - NHoodSize)             # element-wise maximum
        end = np.minimum(H.shape, indexMat + NHoodSize + 1)     # element-wise minimum
        Hslice = map(lambda x: slice(x[0], x[1]), zip(start, end))
        H[Hslice] = 0

        # restore the center (which is the one we want)
        H[indexMat] = value

        peaks.append(indexMat)

        if len(peaks) == numpeaks:
            break
    
    return peaks
