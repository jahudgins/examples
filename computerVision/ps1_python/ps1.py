# % ps1
# Jonathan Hudgins (jhudgins8@gatech.edu)
# GTID: 903050550
#
# Started from templates provide by Jeffrey Chenoweth
#

import cv2
import numpy as np
import copy

from find_circles import find_circles
from hough_circles_acc import hough_circles_acc
from hough_peaks import hough_peaks
from hough_lines_acc import hough_lines_acc
from hough_lines_draw import hough_lines_draw, hough_peak_to_line

def part1():
    print "part1a"
    # %% 1-a
    img = cv2.imread('input/ps1-input0.png', cv2.IMREAD_UNCHANGED)  # already grayscale

    # %% TODO: Compute edge image img_edges
    img_edges = cv2.Canny(img, 100, 200, L2gradient=True)

    cv2.imwrite('output/ps1-1-a-1.png', img_edges) # save as output/ps1-1-a-1.png
    
    return img, img_edges


def hough_process(img, img_edges, accumulator_filename, highlight_filename, lines_filename,
                    RhoResolution=1.0, Theta=np.arange(-90., 90.),
                    numpeaks=1, Threshold=None, NHoodSize=None):
    # %% 2-a
    (H, theta, rho) = hough_lines_acc(img_edges, RhoResolution, Theta)  # defined in hough_lines_acc.py

    # %% TODO: Plot/show accumulator array H, save as output/ps1-2-a-1.png
    min = H.min()
    max = H.max()
    accumulator = np.uint8((H - min) * 255 / (max - min))
    if accumulator_filename:
        cv2.imwrite(accumulator_filename, accumulator)


    # %% 2-b
    Hcopy = copy.deepcopy(H)
    peaks = hough_peaks(Hcopy, numpeaks, Threshold, NHoodSize)  # defined in hough_peaks.py

    # %% TODO: Highlight peak locations on accumulator array, save as output/ps1-2-b-1.png
    for peak in peaks:
        cv2.circle(accumulator, (peak[1], peak[0]), radius=4, color=255, thickness=2)

    if highlight_filename:
        cv2.imwrite(highlight_filename, accumulator)

    # %% TODO: Rest of your code here

    img_lines = hough_lines_draw(img, lines_filename, peaks, rho, theta)


def part3():
    """
    3. Now we're going to add some noise.

    3.a.
    Use ps1-input0-noise.png - same image as before, but with noise.
    Compute a modestly smoothed version of this image by using a Gaussian filter.
    Make sigma at least a few pixels big.
    Output: Smoothed image: ps1-3-a-1.png
    """
    print "part3a"
    img_noisy = cv2.imread('input/ps1-input0-noise.png')
    img_noisy = cv2.cvtColor(img_noisy, cv2.COLOR_RGB2GRAY)
    img_smoothed = cv2.GaussianBlur(img_noisy, (0, 0), 4)
    cv2.imwrite('output/ps1-3-a-1.png', img_smoothed)

    """
    cv2.imshow('noisy', img_noisy)
    cv2.imshow('smoothed-4', img_smoothed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """

    """
    3.b.
    Using an edge operator of your choosing, create a binary edge image
    for both the original image (ps1-input0-noise.png) and the smoothed version above.
    Output: Two edge images: ps1-3-b-1.png (from original), ps1-3-b-2.png (from smoothed)
    """
    print "part3b"
    img_noisy_edges = cv2.Canny(img_noisy, 100, 200, L2gradient=True)
    img_smoothed_edges = cv2.Canny(img_smoothed, 15, 45, L2gradient=True)
    cv2.imwrite('output/ps1-3-b-1.png', img_noisy_edges)
    cv2.imwrite('output/ps1-3-b-2.png', img_smoothed_edges)

    """
    3.c.
    Now apply your Hough method to the smoothed version of the edge image.
    Your goal is to adjust the filtering, edge finding, and Hough algorithms
    to find the lines as best you can in this test case.
    Output:
    - Hough accumulator array image with peaks highlighted: ps1-3-c-1.png 
    - Intensity image (original one with the noise) with lines drawn on them: ps1-3-c-2.png
    - Text response: Describe what you had to do to get the best result you could.
    """
    print "part3c"
    hough_process(img_noisy, img_smoothed_edges, None, 'output/ps1-3-c-1.png', 'output/ps1-3-c-2.png', numpeaks=10)


def part4():
    """
    4.
    For this question use: ps1-input1.png
    4.a.
    This image has objects in it whose boundaries are circles (coins) or lines (pens).
    For this question  you're still finding lines. Load/create a monochrome version of
    the image (you can pick a single color channel or use a built-in color to grayscale
    conversion function), and compute a modestly smoothed version of this image by using
    a Gaussian filter. Make sigma at least a few pixels big.
    Output: Smoothed monochrome image: ps1-4-a-1.png
    """
    print "part4a"
    img = cv2.imread('input/ps1-input1.png', cv2.IMREAD_GRAYSCALE)
    img_smoothed = cv2.GaussianBlur(img, (0, 0), 2.5)
    cv2.imwrite('output/ps1-4-a-1.png', img_smoothed)

    """
    4.b.
    Create an edge image for the smoothed version above.
    Output: Edge image: ps1-4-b-1.png
    """
    print "part4b"
    img_edges = cv2.Canny(img_smoothed, 15, 45, L2gradient=True)
    cv2.imwrite('output/ps1-4-b-1.png', img_edges)

    """
    4.c.
    Apply your Hough algorithm to the edge image to find lines along the pens.
    Draw the lines in color on the  original monochrome (not edge) image.
    The lines can extend to the edges of the image.
    Output:
    - Hough accumulator array image with peaks highlighted: ps1-4-c-1.png
    - Original monochrome image with lines drawn on it: ps1-4-c-2.png
    - Text response: Describe what you had to do to get the best result you could.
    """
    print "part4c"
    hough_process(img, img_edges, None, 'output/ps1-4-c-1.png', 'output/ps1-4-c-2.png', numpeaks=10, NHoodSize=np.array((10, 3)))


def part5():
    """
    5.
    5.a.
    Now write a circle finding version of the Hough transform.
    You can implement either the single point method or the
    point plus gradient method. WARNING: This part may be hard!!! Leave extra time!
    If you find your arrays getting too big (hint, hint) you might try
    make the range of radii very small to start with and see if you can
    find one size circle. Then maybe try the different sizes.

    Implement hough_circles_acc to compute the accumulator array for a given radius.
    Using the same original image (monochrome) as above (ps1-input1.png),a
    smooth it, find the edges (or directly use edge image from 4-b above),
    and try calling your function with radius = 20:

            H = hough_circles_acc(img_edges, 20)

    This should return an accumulator H of the same size as the supplied image.
    Each pixel value of the accumulator array should be proportional
    to the likelihood of a circle of the given radius being present
    (centered) at that location. Find circle centers by using the
    same peak finding function:

            centers = hough_peaks(H, 10)

    Function file: hough_circles_acc.m (hough_peaks.m should already be there)
    Output:
    - Smoothed image: ps1-5-a-1.png (this may be identical to  ps1-4-a-1.png)
    - Edge image: ps1-5-a-2.png (this may be identical to  ps1-4-b-1.png)
    - Original monochrome image with the circles drawn in color:  ps1-5-a-3.png
    """
    print "part5a"
    img = cv2.imread('input/ps1-input1.png', cv2.IMREAD_GRAYSCALE)
    img_smoothed = cv2.GaussianBlur(img, (0, 0), 2.5)
    cv2.imwrite('output/ps1-5-a-1.png', img_smoothed)

    img_edges = cv2.Canny(img_smoothed, 15, 45, L2gradient=True)
    cv2.imwrite('output/ps1-5-a-2.png', img_edges)

    img_circles = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    radius = 20
    H = hough_circles_acc(img_edges, radius)
    peaks = hough_peaks(H, numpeaks=10, Threshold=0.95 * H.max())
    map(lambda x: cv2.circle(img_circles, (x[1], x[0]), radius, (0, 255, 0)), peaks)
    cv2.imwrite('output/ps1-5-a-3.png', img_circles)

    # tweaked theta range
    # tweak threshold

    """
    5.b.
    Implement a function  find_circles that combines the above two steps,
    searching for circles within a given radius range, and returns circle
    centers along with their radii:
            [centers, radii] = find_circles(img_edges, [20 50])

    Function file: find_circles.m
    Output:
    - Original monochrome image with the circles drawn in color:  ps1-5-b-1.png
    - Text response: Describe what you had to do to find circles.
    """
    print "part5b"
    img_circles = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    [centers, radii] = find_circles(img_edges, [19, 50])
    for center, radius in zip(centers, radii):
        cv2.circle(img_circles, (center[1], center[0]), radius, (0, 255, 0))
    cv2.imwrite('output/ps1-5-b-1.png', img_circles)

    # added minimum of 3 for NHoodSize
    # fixed peaks to work for any number of dimensions
    # changed theta range to be 20 degree increments (max of 18)
    # experimented with variety of thresholds
        

def part6():
    """
    6.
    6.a.
    More realistic images. Now that you have Hough methods working, we're going to
    try them on images that have clutter in them - visual elements that are not
    part of the objects to be detected. The image to use is ps1-input2.png.

    Apply your line finder. Use a smoothing filter and edge detector that seems to
    work best in terms of finding all the pen edges. Don't worry (until b)
    about whether you are finding other lines.
    Output: Smoothed image you used with the Hough lines drawn on them: ps1-6-a-1.png
    """
    print "part6a"
    img = cv2.imread('input/ps1-input2.png', cv2.IMREAD_GRAYSCALE)
    img_smoothed = cv2.GaussianBlur(img, (0, 0), 2)
    img_edges = cv2.Canny(img_smoothed, 15, 45, L2gradient=True)
    hough_process(img_smoothed, img_edges, None, None, 'output/ps1-6-a-1.png', numpeaks=30, NHoodSize=np.array((15,3)))

    """
    6.b.
    Likely the last step found lines that are not the boundaries of the pens.
    What are the problems present?
    Output: Text response
    """
    """
    There are many legitimate lines in the photo. If we are just looking for the pens, we can look
    for 2 parallel lines (about 20 pixels apart) that take more than ~30% of the photo height.
    """
    

    """
    6.c.
    Attempt to find only the lines that are the *boundaries* of the pen. 
    Three operations you need to try are better thresholding in finding the
    lines (look for stronger edges), checking the minimum length of the line,
    looking for nearby parallel lines.
    Output: Smoothed image with new Hough lines drawn: ps1-6-c-1.png
    """
    print "part6c"
    (H, theta, rho) = hough_lines_acc(img_edges)
    Hcopy = copy.deepcopy(H)
    peaks = hough_peaks(Hcopy, numpeaks=30, NHoodSize=np.array((15,3)))

    # finding exact line length is more difficult, so I just use the number of
    # hits to approximate line length (which is the number of samples that are on a given
    # line and also the threshold)

    # let's match parallel lines within 50 pixels
    lines = map(lambda x: hough_peak_to_line(img_edges, x, rho, theta), peaks)
    matching_lines = list()
    matching_dist = 50
    slope_threshold = 0.05
    while len(lines) > 1:
        base_line = lines.pop()
        for cmp_line in lines:
            dist_start = np.linalg.norm(np.array(base_line[0]) - np.array(cmp_line[0]))
            base_slope = approx_slope(base_line)
            cmp_slope = approx_slope(cmp_line)
            if dist_start < matching_dist and abs((base_slope - cmp_slope)/base_slope) < slope_threshold:
                matching_lines.append((base_line, cmp_line))
                lines.remove(cmp_line)
                break

    img_lines = cv2.cvtColor(img_smoothed, cv2.COLOR_GRAY2RGB)
    for line_pair in matching_lines:
        for line in line_pair:
            cv2.line(img_lines, line[0], line[1], (0, 255, 0))
            
    cv2.imwrite('output/ps1-6-c-1.png', img_lines)
                    
def approx_slope(line):
    deltaY = line[0][1] - line[1][1]
    if deltaY == 0:
        deltaY = 1
    return (line[0][0] - line[1][0])/float(deltaY)
                

def peak_length(peak, endpoint_dict):
    points = endpoint_dict[peak]
    maxy_length = np.linalg.norm(np.array(points[0]) - np.array(points[1]))
    maxx_length = np.linalg.norm(np.array(points[2]) - np.array(points[3]))
    return max(maxy_length, maxx_length)
        
def part7():
    """
    7.
    7.a.
    Finding circles on the same clutter image (ps1-input2.png).  
    Apply your circle finder. Use a smoothing filter that seems to work
    best in terms of finding all the coins.
    Output:  the smoothed image you used with the circles drawn on them: ps1-7-a-1.png
    """
    print "part7a"
    img = cv2.imread('input/ps1-input2.png', cv2.IMREAD_GRAYSCALE)
    img_smoothed = cv2.GaussianBlur(img, (0, 0), 2.5)
    img_edges = cv2.Canny(img_smoothed, 15, 45, L2gradient=True)

    [centers, radii] = find_circles(img_edges, [19, 50])
    img_circles = cv2.cvtColor(img_smoothed, cv2.COLOR_GRAY2RGB)
    for center, radius in zip(centers, radii):
        cv2.circle(img_circles, (center[1], center[0]), radius, (0, 255, 0), thickness=2)
    cv2.imwrite('output/ps1-7-a-1.png', img_circles)

    """
    7.b.
    Are there any false alarms? How would/did you get rid of them?
    Output: Text response (if you did these steps, mention where they are
    in the code by file, line no. and also include brief snippets)
    """


def part8():
    """
    8.
    8.a.
    Sensitivity to distortion. There is a distorted version of the scene at ps1-input3.png.
    Apply the line and circle finders to the distorted image. Can you find lines? Circles?  
    Output: Monochrome image with lines and circles (if any) found: ps1-8-a-1.png
    """
    print "part8a"
    img = cv2.imread('input/ps1-input3.png', cv2.IMREAD_GRAYSCALE)
    img_smoothed = cv2.GaussianBlur(img, (0, 0), 2.5)
    img_edges = cv2.Canny(img_smoothed, 15, 45, L2gradient=True)

    (H, theta, rho) = hough_lines_acc(img_edges)
    peaks = hough_peaks(H, numpeaks=10,  NHoodSize=np.array((10, 3)))
    img_output = hough_lines_draw(img_smoothed, 'output/ps1-8-a-1.png', peaks, rho, theta)

    [centers, radii] = find_circles(img_output, [19, 50])
    for center, radius in zip(centers, radii):
        cv2.circle(img_output, (center[1], center[0]), radius, (0, 255, 0), thickness=2)
    cv2.imwrite('output/ps1-8-a-1.png', img_output)

    """
    Lines should be no problem, because a line will remain a line under linear transformations (camera tilt).
    The cirlces will be a problem though. I could try to change the circle formula to an ellipse.
    I could relax the threshold for the circle (but that will also increase false positives).
    Another strategy would be to transform the image -- but that would only work for items
    that are in the same plane. Another strategy would be to add another hough dimension: orientation.
    Orientation probably deserves 2 dimensions, yaw and pitch (roll is not needed because of circle
    symmetry.
    """

    """
    8.b.
    What might you do to fix the circle problem? 
    Output: Text response describing what you might try
    """

    """
    8.c.
    EXTRA CREDIT:  Try to fix the circle problem (THIS IS HARD).
    Output:
    - Image that is the best shot at fixing the circle problem, with circles found: ps1-8-c-1.png
    - Text response describing what tried and what worked best (with snippets).
    """


if __name__=='__main__':
    img, img_edges = part1()
    hough_process(img, img_edges, 'output/ps1-2-a-1.png', 'output/ps1-2-b-1.png', 'output/ps1-2-c-1.png', numpeaks=10)
    part3()
    part4()
    part5()
    part6()
    part7()
    part8()

# Reference
#img_edges = cv2.Canny(img, minVal=100, maxVal=200, aperture_size=3, L2gradient=True)
#cv2.imshow('original', img)
#cv2.imshow('edges', img_edges)
#cv2.imshow('accumulator', accumulator)
#cv2.imshow('peaks', accumulator)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
