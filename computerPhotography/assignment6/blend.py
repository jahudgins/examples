import numpy as np
import scipy.ndimage
import cv2
import os
import assignment6_test

"""
def gaussian(sigma, size):
    m = np.zeros((size, size))
    m[size/2, size/2] = 1
    return scipy.ndimage.gaussian_filter(m, sigma)
"""


if __name__ == "__main__":
    dirname = "../../images/seasons"
    white_img = cv2.imread(os.path.join(dirname, "sunriseSantaMonica.jpg"))
    white_img = cv2.resize(white_img, (white_img.shape[1]/4, white_img.shape[0]/4), interpolation=cv2.INTER_LANCZOS4)
    black_img = cv2.imread(os.path.join(dirname, "winterSkyWinterPark.jpg"))
    black_img = cv2.resize(black_img, (white_img.shape[1], white_img.shape[0]), interpolation=cv2.INTER_LANCZOS4)

    mask = np.zeros((100, 100, 3), np.uint8)
    points = np.matrix([  (2*mask.shape[1]/3, 0),
                (mask.shape[1], 0),
                (mask.shape[1], mask.shape[0]),
                (mask.shape[1]/3, mask.shape[0])])
    cv2.fillConvexPoly(mask, points, (255, 255, 255))

    blur_sigma = max(mask.shape) / 10.
    mask_smoothed = scipy.ndimage.gaussian_filter(mask, blur_sigma)
    mask_scaled = cv2.resize(mask_smoothed, (white_img.shape[1], white_img.shape[0]), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite('mask_scaled.png', mask_scaled)

    black_img = black_img.astype(float)
    white_img = white_img.astype(float)
    mask_scaled = mask_scaled.astype(float) / 255

    out_layers = []
    simple_layers = []
    for ch in range(3):
        lp_black, lp_white, gp_black, gp_white, gp_mask, out_pyr, out_img = \
                assignment6_test.run_blend(black_img[:,:,ch], white_img[:,:,ch], mask_scaled[:,:,ch])
        out_layers.append(out_img)

        simple_layers.append(np.multiply(1-mask_scaled[:,:,ch], black_img[:,:,ch]) + np.multiply(mask_scaled[:,:,ch], white_img[:,:,ch]))

    out_img = cv2.merge(out_layers)
    simple_img = cv2.merge(simple_layers)

    cv2.imwrite('mask.png', mask)
    cv2.imwrite('mask_smoothed.png', mask_smoothed)
    cv2.imwrite('blended.png', out_img)
    cv2.imwrite('simple_blend.png', simple_img)
