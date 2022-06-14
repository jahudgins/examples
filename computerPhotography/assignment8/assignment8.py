# ASSIGNMENT 8
# Jonthan Hudgins
# CS6475 Spring 2015 OMS
# GTID: 903050550

import numpy as np
import scipy as sp
import scipy.signal
import scipy.special
import cv2
import assignment6_test

blendmodes=['overwrite', 'average', 'sigmoid', 'laplacian']

# Import ORB as SIFT to avoid confusion.
try:
    from cv2 import ORB as SIFT
except ImportError:
    try:
        from cv2 import SIFT
    except ImportError:
        try:
            SIFT = cv2.ORB_create
        except:
            raise AttributeError("Your OpenCV(%s) doesn't have SIFT / ORB."
                                 % cv2.__version__)


""" Assignment 8 - Panoramas

This file has a number of functions that you need to fill out in order to
complete the assignment. Please write the appropriate code, following the
instructions on which functions you may or may not use.

GENERAL RULES:
    1. DO NOT INCLUDE code that saves, shows, displays, writes the image that
    you are being passed in. Do that on your own if you need to save the images
    but the functions should NOT save the image to file. (This is a problem
    for us when grading because running 200 files results a lot of images being
    saved to file and opened in dialogs, which is not ideal). Thanks.

    2. DO NOT import any other libraries aside from the three libraries that we
    provide. You may not import anything else, you should be able to complete
    the assignment with the given libraries (and in most cases without them).

    3. DO NOT change the format of this file. Do not put functions into classes,
    or your own infrastructure. This makes grading very difficult for us. Please
    only write code in the allotted region.
"""

def getImageCorners(image):
    """ For an input image, return its four corners.

    You should be able to do this correctly without instruction. If in doubt,
    resort to the testing framework. The order in which you store the corners
    does not matter.

    Note: The reasoning for the shape of the array can be explained if you look
    at the documentation for cv2.perspectiveTransform which we will use on the
    output of this function. Since we will apply the homography to the corners
    of the image, it needs to be in that format.

    Another note: When storing your corners, they are assumed to be in the form
    (X, Y) -- keep this in mind and make SURE you get it right.

    Args:
        image (numpy.ndarray): Input can be a grayscale or color image.

    Returns:
        corners (numpy.ndarray): Array of shape (4, 1, 2). Type of values in the
                                 array is np.float32.
    """
    corners = np.zeros((4, 1, 2), dtype=np.float32)
    # WRITE YOUR CODE HERE

    corners = np.array([[[0, 0]],               [[0, image.shape[0]]],
                        [[image.shape[1], 0]],  [[image.shape[1], image.shape[0]]]]).astype(np.float32)

    return corners
    # END OF FUNCTION

def findMatchesBetweenImages(image_1, image_2, num_matches):
    """ Return the top list of matches between two input images.

    Note: You will not be graded for this function. This function is almost
    identical to the function in Assignment 7 (we just parametrized the number
    of matches). We expect you to use the function you wrote in A7 here. We will
    also release a solution for how to do this after A7 submission has closed.

    If your code from A7 was wrong, don't worry, you will not lose points in
    this assignment because your A7 code was wrong (hence why we will provide a
    solution for you after A7 closes).

    This function detects and computes SIFT (or ORB) from the input images, and
    returns the best matches using the normalized Hamming Distance through brute
    force matching.

    Args:
        image_1 (numpy.ndarray): The first image (grayscale).
        image_2 (numpy.ndarray): The second image. (grayscale).
        num_matches (int): The number of desired matches. If there are not
                           enough, return as many matches as you can.

    Returns:
        image_1_kp (list): The image_1 keypoints, the elements are of type
                           cv2.KeyPoint.
        image_2_kp (list): The image_2 keypoints, the elements are of type 
                           cv2.KeyPoint.
        matches (list): A list of matches, length 'num_matches'. Each item in 
                        the list is of type cv2.DMatch. If there are less 
                        matches than num_matches, this function will return as
                        many as it can.

    """
    # matches - type: list of cv2.DMath
    matches = None
    # image_1_kp - type: list of cv2.KeyPoint items.
    image_1_kp = None
    # image_1_desc - type: numpy.ndarray of numpy.uint8 values.
    image_1_desc = None
    # image_2_kp - type: list of cv2.KeyPoint items.
    image_2_kp = None
    # image_2_desc - type: numpy.ndarray of numpy.uint8 values.
    image_2_desc = None

    # COPY YOUR CODE FROM A7 HERE.

    sift = SIFT()
    image_1_kp, image_1_desc = sift.detectAndCompute(image_1, None)
    image_2_kp, image_2_desc = sift.detectAndCompute(image_2, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(image_1_desc, image_2_desc)
    matches.sort(key = lambda x:x.distance)
    matches = matches[:num_matches]

    return image_1_kp, image_2_kp, matches
    # END OF FUNCTION.

def findHomography(image_1_kp, image_2_kp, matches):
    """ Returns the homography between the keypoints of image 1, image 2, and
        its matches.

    Follow these steps:
        1. Iterate through matches and:
            1a. Get the x, y location of the keypoint for each match. Look up
                the documentation for cv2.DMatch. Image 1 is your query image,
                and Image 2 is your train image. Therefore, to find the correct
                x, y location, you index into image_1_kp using match.queryIdx,
                and index into image_2_kp using match.trainIdx. The x, y point
                is stored in each keypoint (look up documentation).
            1b. Set the keypoint 'pt' to image_1_points and image_2_points, it
                should look similar to this inside your loop:
                    image_1_points[match_idx] = image_1_kp[match.queryIdx].pt
                    # Do the same for image_2 points.

        2. Call cv2.findHomography and pass in image_1_points, image_2_points,
           use method=cv2.RANSAC and ransacReprojThreshold=5.0. I recommend
           you look up the documentation on cv2.findHomography to better
           understand what these parameters mean.
        3. cv2.findHomography returns two values, the homography and a mask.
           Ignore the mask, and simply return the homography.

    Args:
        image_1_kp (list): The image_1 keypoints, the elements are of type
                           cv2.KeyPoint.
        image_2_kp (list): The image_2 keypoints, the elements are of type 
                           cv2.KeyPoint.
        matches (list): A list of matches. Each item in the list is of type
                        cv2.DMatch.
    Returns:
        homography (numpy.ndarray): A 3x3 homography matrix. Each item in
                                    the matrix is of type numpy.float64.
    """
    image_1_points = np.zeros((len(matches), 1, 2), dtype=np.float32)
    image_2_points = np.zeros((len(matches), 1, 2), dtype=np.float32)

    # WRITE YOUR CODE HERE.

    for idx, match in enumerate(matches):
        image_1_points[idx] = image_1_kp[match.queryIdx].pt
        image_2_points[idx] = image_2_kp[match.trainIdx].pt

    homography, mask = cv2.findHomography(image_1_points, image_2_points, cv2.RANSAC, ransacReprojThreshold=5)

    # Replace this return statement with the homography.
    return homography
    # END OF FUNCTION

def blendImagePair(warped_image, image_2, point, blendmode='overwrite', translated_corners=None):
    """ This is the blending function. We provide a basic implementation of
    this function that we would like you to replace.

    This function takes in an image that has been warped and an image that needs
    to be inserted into the warped image. Lastly, it takes in a point where the
    new image will be inserted.

    The current method we provide is very simple, it pastes in the image at the
    point. We want you to replace this and blend between the images.

    We want you to be creative. The most common implementation would be to take
    the average between image 1 and image 2 only for the pixels that overlap.
    That is just a starting point / suggestion but you are encouraged to use
    other approaches.

    Args:
        warped_image (numpy.ndarray): The image provided by cv2.warpPerspective.
        image_2 (numpy.ndarray): The image to insert into the warped image.
        point (numpy.ndarray): The point (x, y) to insert the image at.

    Returns:
        image: The warped image with image_2 blended into it.
    """
    output_image = warped_image
    # REPLACE THIS WITH YOUR BLENDING CODE.

    # find minimal range of overlap
    translated_corners = translated_corners.astype(int)
    x_min_idx = np.ix_([0,1,4,5])
    x_max_idx = np.ix_([2,3,6,7])
    blend_x_min = translated_corners[x_min_idx, :, 0].max()
    blend_x_max = translated_corners[x_max_idx, :, 0].min()
    blend_x_mid = int((blend_x_min + blend_x_max) / 2)

    y_min_idx = np.ix_([0,2,4,6])
    y_max_idx = np.ix_([1,3,5,7])
    crop_y_min = translated_corners[y_min_idx, :, 1].max()
    crop_y_max = translated_corners[y_max_idx, :, 1].min()

    # create a sigmoid across range of x
    x_range = np.linspace(-50, 50, output_image.shape[1]).astype(np.float32)
    x_range = x_range - x_range[blend_x_mid]

    sigmoid = scipy.special.expit(x_range)

    if blendmode == 'overwrite':
        output_image[point[1]:point[1] + image_2.shape[0],
                     point[0]:point[0] + image_2.shape[1]] = image_2
    elif blendmode == 'average':
        mask = np.zeros(output_image.shape).astype(np.float32)
        mask[point[1]:point[1] + image_2.shape[0],
             point[0]:point[0] + image_2.shape[1]] = 0.5
        mask[np.where(output_image == [0,0,0])] = 1
        stage_image = np.zeros(output_image.shape).astype(np.float32)
        stage_image[point[1]:point[1] + image_2.shape[0],
                    point[0]:point[0] + image_2.shape[1]] = image_2
        output_image = np.multiply(1-mask, output_image) + np.multiply(mask, stage_image)
    elif blendmode == 'sigmoid':
        sigmoid = scipy.special.expit(x_range)


        ones = np.ones(output_image.shape).astype(np.float32)
        mask = np.multiply(ones, sigmoid.reshape((1, output_image.shape[1], 1)))
        output_image = np.multiply(1-mask, output_image)

        stage_image = np.zeros(output_image.shape).astype(np.float32)
        stage_image[point[1]:point[1] + image_2.shape[0],
                    point[0]:point[0] + image_2.shape[1]] = image_2
        stage_image = np.multiply(mask, stage_image)
        output_image = output_image + stage_image

        output_image = output_image[crop_y_min:crop_y_max,:,:]

    elif blendmode == 'laplacian':
        ones = np.ones(output_image.shape[0:2]).astype(np.float32)
        mask = np.multiply(ones, sigmoid.reshape((1, output_image.shape[1])))

        stage_image = np.zeros(output_image.shape).astype(np.float32)
        stage_image[point[1]:point[1] + image_2.shape[0],
                    point[0]:point[0] + image_2.shape[1]] = image_2

        out_layers = []
        simple_layers = []
        for ch in range(3):
            lp_output, lp_image, gp_output, gp_image, gp_mask, out_pyr, out_img = \
                    assignment6_test.run_blend(output_image[:,:,ch], stage_image[:,:,ch], mask)
            out_layers.append(out_img)

        output_image = cv2.merge(out_layers)
        output_image = output_image[crop_y_min:crop_y_max,:,:]

    return output_image.astype(np.uint8)
    # END OF FUNCTION

def warpImagePair(image_1, image_2, homography, blendmode='overwrite'):
    """ Warps image 1 so it can be blended with image 2 (stitched).

    Follow these steps:
        1. Obtain the corners for image 1 and image 2 using the function you
        wrote above.
        
        2. Transform the perspective of the corners of image 1 by using the
        image_1_corners and the homography to obtain the transformed corners.
        
        Note: Now we know the corners of image 1 and image 2. Out of these 8
        points (the transformed corners of image 1 and the corners of image 2),
        we want to find the minimum x, maximum x, minimum y, and maximum y. We
        will need this when warping the perspective of image 1.

        3. Join the two corner arrays together (the transformed image 1 corners,
        and the image 2 corners) into one array of size (8, 1, 2).

        4. For the first column of this array, find the min and max. This will
        be your minimum and maximum X values. Store into x_min, x_max.

        5. For the second column of this array, find the min and max. This will
        be your minimum and maximum Y values. Store into y_min, y_max.

        6. Create a translation matrix that will shift the image by the required
        x_min and y_min (should be a numpy.ndarray). This looks like this:
            [[1, 0, -1 * x_min],
             [0, 1, -1 * y_min],
             [0, 0, 1]]

        Note: We'd like you to explain the reasoning behind multiplying the
        x_min and y_min by negative 1 in your writeup.

        7. Compute the dot product of your translation matrix and the homography
        in order to obtain the homography matrix with a translation.

        8. Then call cv2.warpPerspective. Pass in image 1, the dot product of
        the matrix computed in step 6 and the passed in homography and a vector
        that will fit both images, since you have the corners and their max and
        min, you can calculate it as (x_max - x_min, y_max - y_min).

        9. To finish, you need to blend both images. We have coded the call to
        the blend function for you.

    Args:
        image_1 (numpy.ndarray): Left image.
        image_2 (numpy.ndarray): Right image.
        homography (numpy.ndarray): 3x3 matrix that represents the homography
                                    from image 1 to image 2.

    Returns:
        output_image (numpy.ndarray): The stitched images.
    """
    # Store the result of cv2.warpPerspective in this variable.
    warped_image = None
    # The minimum and maximum values of your corners.
    x_min = 0
    y_min = 0
    x_max = 0
    y_max = 0

    # WRITE YOUR CODE HERE

    corners_1 = getImageCorners(image_1)
    corners_2 = getImageCorners(image_2)
    homo_corners_1 = np.concatenate((corners_1, np.ones((4,1,1))), axis=2)
    transformed_corners_1 = np.dot(homo_corners_1, homography.T)
    transformed_corners_1[:,0,:] = np.multiply(transformed_corners_1[:,0,:], 1/transformed_corners_1[:,:,2])

    # drop the homogenous
    transformed_corners_1 = transformed_corners_1[:,:,0:2]
    corners = np.vstack((transformed_corners_1, corners_2))

    x_min = corners[:,:,0].min()
    x_max = corners[:,:,0].max()

    y_min = corners[:,:,1].min()
    y_max = corners[:,:,1].max()

    translation = np.matrix([   [1, 0, -1 * x_min],
                                [0, 1, -1 * y_min],
                                [0, 0, 1]])

    homography_translate = np.dot(translation, homography)

    warped_image = cv2.warpPerspective(image_1, homography_translate, (int(x_max - x_min), int(y_max - y_min)))

    translated_corners = corners - np.multiply(np.ones(corners.shape), np.array([[[x_min, y_min]]]))

    # END OF CODING
    output_image = blendImagePair(warped_image, image_2, (-1 * x_min, -1 * y_min), blendmode, translated_corners)
    return output_image

# Some simple testing.
# image_1 = cv2.imread("images/source/panorama_1/1.jpg")
# image_2 = cv2.imread("images/source/panorama_1/2.jpg")
# image_1_kp, image_2_kp, matches = findMatchesBetweenImages(image_1, image_2,
#                                                            20)
# homography = findHomography(image_1_kp, image_2_kp, matches)
# result = warpImagePair(image_1, image_2, homography)
# cv2.imwrite("images/output/panorama_1_result.jpg", result)
