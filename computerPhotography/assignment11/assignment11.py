# ASSIGNMENT 11
# Jonathan Hudgins

""" Assignment 11 - Video Textures

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

import numpy as np
import cv2
import scipy.signal


def videoVolume(images):
    """ Create a video volume from the image list.

    Note: Simple function to convert a list to a 4D numpy array, you should know
    how to do this.

    Args:
        images (list): A list of frames. Each element of the list contains a
                       numpy array of a colored image. You may assume that each
                       frame has the same shape, (rows, cols, 3).

    Returns:
        output (numpy.ndarray): A 4D numpy array. This array should have
                                dimensions (num_frames, rows, cols, 3) and
                                dtype np.uint8.
    """
    output = np.zeros((len(images), images[0].shape[0], images[0].shape[1],
                      images[0].shape[2]), dtype=np.uint8)

    # WRITE YOUR CODE HERE.

    output = np.concatenate(images)
    output = output.reshape((len(images), images[0].shape[0], images[0].shape[1], images[0].shape[2]))

    # END OF FUNCTION.
    return output

def sumSquaredDifferences(video_volume):
    """ Compute the sum of squared differences for each pair of frames in video
        volume.

    Suggested Instructions:
        1. Create a for loop that goes through the video volume. Create a
           variable called cur_frame.
            1a. Create another for loop that goes through the video volume
                again. Create a variable called comparison_frame.
                1a-i. Inside this loop, compute this mathematical statement.
                    ssd = sum ( (cur_frame - comparison_frame)^2 )
                1a-ii. Set output[i, j] = ssd.

    Hint: Remember the matrix is symmetrical, so when you are computing the ssd
    at i, j, its the same as computing the ssd at j, i so you shouldn't have to
    do the math twice. This speeds up the function by 2.

    Args:
        video_volume (numpy.ndarray): A 4D numpy array with dimensions
                                      (num_frames, rows, cols, 3). This can be
                                      produced by the videoVolume function.

    Returns:
        output (numpy.ndarray): A square 2d numpy array of dtype float.
                                output[i,j] should contain  the sum of square
                                differences between frames i and j. This matrix
                                is symmetrical with a diagonal of zeros. The
                                values should be np.float.
    """
    
    output = np.zeros((len(video_volume), len(video_volume)), dtype=np.float)
    # WRITE YOUR CODE HERE.

    video_volume = video_volume.astype(np.float32)
    frames = video_volume.shape[0]
    for frame in range(frames):
        for compare_frame in range(frame, frames):
            delta = video_volume[frame,...] - video_volume[compare_frame,...]
            product = np.multiply(delta, delta)
            squared_sum = product.sum()
            output[frame, compare_frame] = squared_sum
            output[compare_frame, frame] = squared_sum

    """
    frames = video_volume.shape[0]
    squared_sums = np.zeros(frames * (frames+1) / 2)
    for frame in range(video_volume.shape[0]):
        delta = video_volume[frame:,...] - np.roll(video_volume, frame, axis=0)[frame:,...]
        product = np.multiply(delta, delta)
        sums = np.sum(product, axis=(1, 2, 3))
        output[frame:,frame] = sums
    """

    # END OF FUNCTION.
    return output

def transitionDifference(ssd_difference):
    """ Compute the transition costs between frames, taking dynamics into
        account.

    Instructions:
        1. Iterate through the rows and columns of ssd difference, ignoring the
           first two values and the last two values.
            1a. For each value at i, j, multiply the binomial filter of length
                five by the weights starting two frames before until two frames
                after, and take the sum of those products.

                i.e. Your weights for frame i are:
                     [weight[i - 2, j - 2],
                      weight[i - 1, j - 1],
                      weight[i, j],
                      weight[i + 1, j + 1],
                      weight[i + 2, j + 2]]

                Multiply that by the binomial filter weights at each i, j to get
                your output.

                It may take a little bit of understanding to get why we are
                computing this, the simple explanation is that to change from
                frame 4 to 5, lets call this ch(4, 5), and we make this weight:

                ch(4, 5) = ch(2, 3) + ch(3, 4) + ch(4, 5) + ch(5, 6) + ch(6, 7)

                This accounts for the weights in previous changes and future
                changes when considering the current frame. 

                Of course, we weigh all these sums by the binomial filter, so
                that the weight ch(4, 5) is still the most important one, but
                hopefully that gives you a better understanding.

    Args:
        ssd_difference (numpy.ndarray): A difference matrix as produced by your
                                        ssd function.

    Returns:
        output (numpy.ndarray): A difference matrix that takes preceding and
                                following frames into account. The output
                                difference matrix should have the same dtype as
                                the input, but be 4 rows and columns smaller,
                                corresponding to only the frames that have valid
                                dynamics.

    Hint: There is an efficient way to do this with 2d convolution. Think about
          the coordinates you are using as you consider the preceding and
          following frame pairings.
    """

    output = np.zeros((ssd_difference.shape[0] - 4,
                       ssd_difference.shape[1] - 4), dtype=ssd_difference.dtype)
    # WRITE YOUR CODE HERE.

    kernel = np.diag(binomialFilter5())
    convolved = scipy.signal.convolve2d(ssd_difference, kernel, 'same')
    output = convolved[2:-2,2:-2]

    # END OF FUNCTION.
    return output


def findBiggestLoop(transition_diff, alpha):
    """ Given the difference matrix, find the longest and smoothest loop that we
      can.

    Args:
        transition_diff (np.ndarray): A square 2d numpy array of dtype float.
                                      Each cell contains the cost of
                                      transitioning from frame i to frame j in
                                      the input video as returned by the
                                      transitionDifference function.

        alpha (float): a parameter for how heavily you should weigh the size of
                       the loop relative to the transition cost of the loop.
                       Larger alphas favor longer loops. Try really big values
                       to see what you get.

    start, end will be the indices in the transition_diff matrix that give the
    maximum score according to the following metric:
        score = alpha * (end - start) - transition_diff[end, start]

    Compute that score for every possible starting and ending index (within the
    size of the transition matrix) and find the largest score.

    See README.html for the scoring function to implement this function.

    Returns:
        start (int): The starting frame number of the longest loop.
        end (int): The final frame number of the longest loop.
    """

    start = 0
    end = 0
    largest_score = 0

    # WRITE YOUR CODE HERE.

    best_start = 0
    best_end = 0
    for start in range(transition_diff.shape[1]):
        for end in range(start+10, transition_diff.shape[0]):
            score = alpha * (end - start) - transition_diff[end, start]
            if score > largest_score:
                largest_score = score
                best_start = start
                best_end = end

    start = best_start
    end = best_end

    # END OF FUNCTION.
    return start, end

def synthesizeLoop(video_volume, start, end):
    """ Pull out the given loop from the input video volume.

    Args:
        video_volume (np.ndarray): A (time, height, width, 3) array, as created
                                   by your videoVolume function.
        start (int): the index of the starting frame.
        end (int): the index of the ending frame.

    Returns:
        output (list): a list of arrays of size (height, width, 3) and dtype
                       np.uint8, similar to the original input the videoVolume
                       function.
    """

    output = [] 
    # WRITE YOUR CODE HERE.


    output = list(video_volume[start:end+1].astype(np.uint8))


    # END OF FUNCTION.
    return output

def binomialFilter5():
    """ Return a binomial filter of length 5.

    Note: This is included for you to use.

    Returns:
        output (numpy.ndarray): A 5x1 numpy array representing a binomial
                                filter.
    """

    return np.array([1 / 16.,  1 / 4.  ,  3 / 8. ,  1 / 4.  ,  1 / 16.],
                    dtype=float)
