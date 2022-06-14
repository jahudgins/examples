# ASSIGNMENT 2
# Jonathan Hudgins (jhudgins8)
# GTID: 903050550

import cv2
import numpy as np
#import scipy as sp

""" Assignment 2 - Basic Image Input / Output / Simple Functionality

This file has a number of functions that you need to fill out in order to
complete the assignment. Please write the appropriate code, following the
instructions on which functions you may or may not use.
"""

def numberOfPixels(image):
    """ This function returns the number of pixels in a grayscale image.

    Note: A grayscale image has one dimension as covered in the lectures. You
    DO NOT have to account for a color image.

    You may use any / all functions to obtain the number of pixels in the image.

    Args:
        image (numpy.ndarray): A grayscale image represented in a numpy array.

    Returns:
        int: The number of pixels in an image.
    """
    # WRITE YOUR CODE HERE.

    return image.shape[0] * image.shape[1]

    # END OF FUNCTION.

def averagePixel(image):
    """ This function returns the average color value of a grayscale image.

    Assignment Instructions: In order to obtain the average pixel, add up all
    the pixels in the image, and divide by the total number of pixels. We advise
    that you use the function you wrote above to obtain the number of pixels!

    You may not use numpy.mean or numpy.average. All other functions are fair
    game.

    Args:
        image (numpy.ndarray): A grayscale image represented in a numpy array.

    Returns:
        int: The average pixel in the image (Range of 0-255).
    """
    # WRITE YOUR CODE HERE.

    average = np.sum(image) / numberOfPixels(image)
    return int(average)

    # END OF FUNCTION.

def convertToBlackAndWhite(image):
    """ This function converts a grayscale image to black and white.

    Assignment Instructions: Iterate through every pixel in the image. If the
    pixel is strictly greater than 128, set the pixel to 255. Otherwise, set the
    pixel to 0. You are essentially converting the input into a 1-bit image, as 
    we discussed in lecture, it is a 2-color image.

    You may NOT use any thresholding functions provided by OpenCV to do this.
    All other functions are fair game.

    Args:
        image (numpy.ndarray): A grayscale image represented in a numpy array.

    Returns:
        numpy.ndarray: The black and white image.
    """
    # WRITE YOUR CODE HERE.

    black_and_white = (image / 129) * 255
    return black_and_white

    # END OF FUNCTION.

def averageTwoImages(image1, image2):
    """ This function averages the pixels of the two input images.

    Assignment Instructions: Obtain the average image by adding up the two input
    images on a per pixel basis and dividing them by two.

    You may use any / all functions to obtain the average image output.

    Note: You may assume image1 and image2 are the SAME size.

    Args:
        image1 (numpy.ndarray): A grayscale image represented in a numpy array.
        image2 (numpy.ndarray): A grayscale image represented in a numpy array.

    Returns:
        numpy.ndarray: The average of image1 and image2.

    """
    # WRITE YOUR CODE HERE.

    average_image = ((image1.astype(int) + image2.astype(int)) / 2).astype(np.uint8)
    return average_image

    # END OF FUNCTION.

def flipHorizontal(image):
    """ This function flips the input image across the horizontal axis.

    Assignment Instructions: Given an input image, flip the image on the
    horizontal axis. This can be interpreted as switching the first and last
    column of the image, the second and second to last column, and so on.

    You may use any / all functions to flip the image horizontally.

    Args:
        image (numpy.ndarray): A grayscale image represented in a numpy array.

    Returns:
        numpy.ndarray: The horizontally flipped image.

    """
    # WRITE YOUR CODE HERE.

    flipped = np.fliplr(image)
    return flipped

    # END OF FUNCTION.

if __name__ == '__main__':
    source1 = cv2.cvtColor(cv2.imread('../../images/Hudgins_J_A1.jpg'), cv2.COLOR_BGR2GRAY)
    source2 = cv2.cvtColor(cv2.imread('../../images/sequoiaRoots.jpg'), cv2.COLOR_BGR2GRAY)

    # resize to be within 512
    # assume similar aspect ratio between source1 and source2
    shape = np.array(source1.shape[:2])
    factor = max(shape)
    shape = shape * 512 / factor
    dim = (shape[1], shape[0])
    
    resized1 = cv2.resize(source1, dim, interpolation=cv2.INTER_LANCZOS4)
    resized2 = cv2.resize(source2, dim, interpolation=cv2.INTER_LANCZOS4)

    cv2.imwrite('input1.png', resized1)
    cv2.imwrite('input2.png', resized2)

    blackAndWhite = convertToBlackAndWhite(resized1)
    average = averageTwoImages(resized1, resized2)
    flippedHorizontal = flipHorizontal(resized1)

    cv2.imwrite('blackAndWhite.png', blackAndWhite)
    cv2.imwrite('average.png', average)
    cv2.imwrite('flipHorizontal.png', flippedHorizontal)

    """
    cv2.imshow('input1.png', resized1)
    cv2.imshow('input2.png', resized2)
    cv2.imshow('blackAndWhite.png', blackAndWhite)
    cv2.imshow('average.png', average)
    cv2.imshow('flipHorizontal.png', flippedHorizontal)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """

