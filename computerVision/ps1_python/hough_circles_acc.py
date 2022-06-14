import numpy as np
import math

def hough_circles_acc(BW, radius):
    # % Compute Hough accumulator array for finding circles.
    # %
    # % BW: Binary (black and white) image containing edge pixels
    # % radius: Radius of circles to look for, in pixels

    # % TODO: Your code here
    H = np.zeros(BW.shape)
    edge_coords = BW.nonzero()
    i = 0
    while i < len(edge_coords[0]):
        y = edge_coords[0][i]
        x = edge_coords[1][i]
        i += 1
        for theta in np.arange(0, 2 * math.pi, 20 * math.pi / 180):
            b = int(y - radius * math.sin(theta))
            a = int(x - radius * math.cos(theta))
            if 0 <= a and a < H.shape[1] and 0 <= b and b < H.shape[0]:
                H[b, a] += 1

    return H
