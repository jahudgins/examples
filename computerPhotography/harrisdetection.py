"""Harris Corner Detection"""

import numpy as np
import cv2

def find_corners(img):
    """Find corners in an image using Harris corner detection method."""
    
    # Convert to grayscale, if necessary
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    
    # Compute Harris corner detector response (params: block size, Sobel aperture, Harris alpha)
    h_response = cv2.cornerHarris(img_gray, 4, 3, 0.04)
    
    # Display Harris response image
    h_min, h_max, _, _ = cv2.minMaxLoc(h_response)  # for thresholding, display scaling
    cv2.imshow("Harris response", np.uint8((h_response - h_min) * (255.0 / (h_max - h_min))))

    # Select corner pixels above threshold
    h_thresh = 0.01 * h_max
    _, h_selected = cv2.threshold(h_response, h_thresh, 1, cv2.THRESH_TOZERO)

    # Pick corner pixels that are local maxima
    nhood_size = 5  # neighborhood size for non-maximal suppression (odd)
    nhood_r = int(nhood_size / 2)  # neighborhood radius = size / 2
    corners = []  # list of corner locations as (x, y, response) tuples
    for y in xrange(h_selected.shape[0]):
        for x in xrange(h_selected.shape[1]):
            if h_selected.item(y, x):
                h_value = h_selected.item(y, x)  # response value at (x, y)
                nhood = h_selected[(y - nhood_r):(y + nhood_r + 1), (x - nhood_r):(x + nhood_r + 1)]
                if not nhood.size:
                    continue  # skip empty neighborhoods (which can happen at edges)
                local_max = np.amax(nhood)  # compute neighborhood maximum
                if h_value == local_max:
                    corners.append((x, y, h_value))  # add to list of corners
                    h_selected[(y - nhood_r):(y + nhood_r), (x - nhood_r):(x + nhood_r)] = 0  # clear
                    h_selected.itemset((y, x), h_value)  # retain maxima value to suppress others

    h_suppressed = np.uint8((h_selected - h_thresh) * (255.0 / (h_max - h_thresh)))
    cv2.imshow("Suppressed Harris response", h_suppressed)
    return corners


def test():
    """Test find_corners() with sample input."""
    
    # Read image
    img = cv2.imread("octagon.png")
    cv2.imshow("Image", img)

    # Find corners
    corners = find_corners(img)
    print "\n".join("{} {}".format(corner[0], corner[1]) for corner in corners)

    # Display output image with corners highlighted
    img_out = img.copy()
    for (x, y, resp) in corners:
        cv2.circle(img_out, (x, y), 1, (0, 0, 255), -1)  # red dot
        cv2.circle(img_out, (x, y), 5, (0, 255, 0), 1)  # green circle
    cv2.imshow("Output", img_out)
