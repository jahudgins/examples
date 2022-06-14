import cv2
import numpy

import argparse

def img_ref(in_filename):
    img = cv2.imread(in_filename)
    print img.size
    print img.shape
    print img.dtype

def swap_red_blue(in_filename, out_filename):
    src = cv2.imread(in_filename)
    b,g,r = cv2.split(src)
    dst = cv2.merge((r,g,b))
    cv2.imwrite(out_filename, dst)
    return dst

def monochrome(index, in_filename, out_filename):
    img = cv2.imread(in_filename)[:,:,index]
    cv2.imwrite(out_filename, img)
    return img

def splice(size, img1, img2, out_filename):
    startX = (img1.shape[0] - size[0]) / 2
    startY = (img1.shape[1] - size[1]) / 2
    section = img1[startX:startX+size[0], startY:startY+size[1]]

    startX = (img2.shape[0] - size[0]) / 2
    startY = (img2.shape[1] - size[1]) / 2
    img2[startX:startX+size[0], startY:startY+size[1]] = section
    cv2.imwrite(out_filename, img2)

    return img2
    

def shift_image(src, offset, out_filename, out_filename2):
    src = src.astype(float) / 255.
    translate_mat = numpy.matrix([  [1.0, 0.0, offset[0]],
                                    [0.0, 1.0, offset[1]]])
    dst = cv2.warpAffine(src, translate_mat, (src.shape[1], src.shape[0]))
    sub = src - dst

    dst = numpy.clip(dst * 255, 0, 255).astype(numpy.uint8)
    sub = numpy.clip(sub * 255, 0, 255).astype(numpy.uint8)

    cv2.imwrite(out_filename, dst)
    cv2.imwrite(out_filename2, sub)


def noise(in_filename, out_filename, out_filename2):
    src = cv2.imread(in_filename).astype(float) / 255.0
    b,g,r = cv2.split(src)
    shape = g.shape
    noise = numpy.random.normal(0, 20/255., shape)
    g_noisy = g + noise
    b_noisy = b + noise

    noisy_green = cv2.merge((b, g_noisy, r))
    noisy_blue = cv2.merge((b_noisy, g, r))

    noisy_green = numpy.clip(noisy_green * 255, 0, 255).astype(numpy.uint8)
    noisy_blue = numpy.clip(noisy_blue * 255, 0, 255).astype(numpy.uint8)

    cv2.imwrite(out_filename, noisy_green)
    cv2.imwrite(out_filename2, noisy_blue)


def normalize(img, center, divisor, multiplier, out_filename):
    dst = (img - center) * (multiplier / divisor) + center
    dst = numpy.clip(dst, 0, 255).astype(numpy.uint8)
    cv2.imwrite(out_filename, dst)
    return dst

if __name__ == '__main__':
    img_ref('output/ps0-1-a-1.png')
    swap_red_blue('output/ps0-1-a-1.png', 'output/ps0-2-a-1.png')
    img1_green = monochrome(1, 'output/ps0-1-a-1.png', 'output/ps0-2-b-1.png')
    img1_red = monochrome(2, 'output/ps0-1-a-1.png', 'output/ps0-2-c-1.png')

    """
    # determine which is better: green, the faces in red are washed out
    cv2.imshow('monochrome green', img1_green)
    cv2.imshow('monochrome red', img1_red)
    cv2.waitKey(0)
    """

    img2_red = cv2.imread('output/ps0-1-a-2.png')[:,:,2]
    splice((100, 100), img1_red, img2_red, 'output/ps0-3-a-1.png')

    shape = img1_green.shape[:2]
    flat = img1_green.reshape(shape[0] * shape[1], 1)
    mean = flat.mean()
    stddev = numpy.std(flat)
    print "min: {}".format(flat.min())
    print "max: {}".format(flat.max())
    print "mean: {}".format(mean)
    print "stddev: {}".format(stddev)

    normalized = normalize(img1_green, mean, stddev, 10, 'output/ps0-4-b-1.png')

    shift_image(img1_green, (-2, 0), 'output/ps0-4-c-1.png', 'output/ps0-4-d-1.png')

    ## noise!
    noise('output/ps0-1-a-1.png', 'output/ps0-5-a-1.png', 'output/ps0-5-b-1.png')
