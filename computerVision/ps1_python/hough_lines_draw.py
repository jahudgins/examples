import cv2
import numpy as np
import copy
import math

def hough_peak_to_line(img, peak, rho, theta):
    # solve for (x0,y0), (x1,y1) from equation
    # r = x * math.cos(t) + y * math.sin(t)
    r = rho[peak[0]]
    t = theta[peak[1]] * math.pi / 180.
    if math.sin(t) == 0:
        y0 = 0
        y1 = img.shape[0]
        x0 = x1 = int(r / math.cos(t) + 0.5)
    else:
        x0 = 0
        x1 = img.shape[1]
        y0 = int((r - x0 * math.cos(t)) / math.sin(t) + 0.5)
        y1 = int((r - x1 * math.cos(t)) / math.sin(t) + 0.5)
    return ((x0, y0), (x1, y1))


def hough_lines_draw(img, outfile, peaks, rho, theta):
    #     % Draw lines found in an image using Hough transform.
    #     %
    #     % img: Image on top of which to draw lines
    #     % outfile: Output image filename to save plot as
    #     % peaks: Qx2 matrix containing row, column indices of the Q peaks found in accumulator
    #     % rho: Vector of rho values, in pixels
    #     % theta: Vector of theta values, in degrees
    # 
    #     % TODO: Your code here
    img_lines = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    lines = map(lambda x: hough_peak_to_line(img, x, rho, theta), peaks)
    map(lambda x: cv2.line(img_lines, x[0], x[1], (0, 255, 0)), lines)

    cv2.imwrite(outfile, img_lines)
    return img_lines
