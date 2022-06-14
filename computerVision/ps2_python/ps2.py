# ps2
# Jonathan Hudgins (jhudgins8@gatech.edu)
# GTID: 903050550
# CS4495 Spring 2015 OMS
import os
import numpy as np
import cv2

from disparity_ssd import disparity_ssd
from disparity_ncorr import disparity_ncorr, disparity_ncorr_mine

def test():
    L = cv2.imread(os.path.join('input', 'pair0-L.png'), cv2.IMREAD_GRAYSCALE) * (1.0 / 255.0)  # grayscale, [0, 1]
    R = cv2.imread(os.path.join('input', 'pair0-R.png'), cv2.IMREAD_GRAYSCALE) * (1.0 / 255.0)  # grayscale, [0, 1]
    #L = L[0:10, 0:10]
    #R = R[0:10, 0:10]
    DL = disparity_ncorr(L, R)
    #DL = disparity_ncorr_mine(L, R)
    cv2.imwrite('base.png', (L * 255).astype(np.uint8))
    write_disparity('test.png', DL)



def write_disparity(filename, disparity):
    maximum = max(abs(disparity.min()), abs(disparity.max()))
    image = disparity * 127 / maximum + 128
    cv2.imwrite(filename, image.astype(np.uint8))

#test()

## 1-a
# Read images
print "part 1"
L = cv2.imread(os.path.join('input', 'pair0-L.png'), 0) * (1.0 / 255.0)  # grayscale, [0, 1]
R = cv2.imread(os.path.join('input', 'pair0-R.png'), 0) * (1.0 / 255.0)

# Compute disparity (using method disparity_ssd defined in disparity_ssd.py)
D_L = disparity_ssd(L, R)
D_R = disparity_ssd(R, L)

# TODO: Save output images (D_L as output/ps2-1-a-1.png and D_R as output/ps2-1-a-2.png)
# Note: They may need to be scaled/shifted before saving to show results properly

write_disparity('output/ps2-1-a-1.png', D_L)
write_disparity('output/ps2-1-a-2.png', D_R)

# TODO: Rest of your code here


"""
2.a.
Now we're going to try this on a real image pair: pair1-L .png and pair1-R .png.  Since these are color images, create grayscale versions. You can use rgb2gray or your own function.
Again apply your SSD match function, and create a disparity image D(y,x) such that L(y,x) = R(y,x+D(y,x)) when matching from left to right. Also match from right to left.
Output: Save disparity images, scaling/shifting as necessary:
- DL(y,x) [matching from left to right] as ps2-2-a-1.png
- DR(y,x) [matching from right to left] as ps2-2-a-2.png
"""

print "part 2"
L = cv2.imread(os.path.join('input', 'pair1-L.png'), cv2.IMREAD_GRAYSCALE) * (1.0 / 255.0)  # grayscale, [0, 1]
R = cv2.imread(os.path.join('input', 'pair1-R.png'), cv2.IMREAD_GRAYSCALE) * (1.0 / 255.0)  # grayscale, [0, 1]
DL = disparity_ssd(L, R)
write_disparity('output/ps2-2-a-1.png', DL)
DR = disparity_ssd(R, L)
write_disparity('output/ps2-2-a-2.png', DR)

"""
2.b.
Also in the input directory are ground truth disparity images pair1-D_dropL .png and pair1-D_R .png.  Compare your results.
Output: Text response - description of the differences between your results and ground truth.
"""



"""
3.a
SSD is not very robust to certain perturbations. We're going to try to see the effect of perturbations:
Using pair1, add some Gaussian noise, either to one image or both. Make the noise sigma big enough that you can tell some noise has been added. Run SSD match again.
Output: Disparity images (DL as ps2-3-a-1.png and DR as ps2-3-a-2.png), text response - analysis of result compared to question 2.
"""

print "part 3a"
Lblurred = cv2.GaussianBlur(L, (7, 7), 4)
DL = disparity_ssd(Lblurred, R)
write_disparity('output/ps2-3-a-1.png', DL)
DR = disparity_ssd(R, Lblurred)
write_disparity('output/ps2-3-a-2.png', DR)

"""
3.b
Instead of the Gaussian noise, increase the contrast (multiplication) of one of the images by just 10%. Run SSD match again.
Output: Disparity images (DL as ps2-3-b-1.png and DR as ps2-3-b-2.png), text response - analysis of result compared to question 2.
"""

print "part 3b"
Lcontrast = L * 1.1 + ((-0.5 * 1.1) + 0.5)
Lcontrast = np.minimum(1.0, np.maximum(0.0, Lcontrast))

DL = disparity_ssd(Lcontrast, R)
write_disparity('output/ps2-3-b-1.png', DL)
DR = disparity_ssd(R, Lcontrast)
write_disparity('output/ps2-3-b-2.png', DR)

"""
4.
Now you're going to use (not implement yourself unless you want)
an improved method, called normalized correlation - this is discussed in the book.
The basic idea is that we think of two image patches as vectors and compute the angle between them - much like normalized dot products.

The explicit dot product of two image patches (treated as flat vectors) is:

This result is then normalized:

4.a
Implement a window matching stereo algorithm using some form of normalized correlation. Again, write this as a function disparity_ncorr(L, R) that returns a disparity image D(y,x) such that L(y,x) = R(y,x+D(y,x)) when matching from left (L) to right (R).
Matlab has its own function normxcorr2(template, A) which implements:


OpenCV has a variety of relevant functions and supported methods as well, such as CV_TM_CCOEFF_NORMED. You MAY use these built-in normalized correlation functions.
Test it on the original images both left to right and right to left (pair1-L.png and pair1-R.png).
Output: Disparity images (DL as ps2-4-a-1.png and DR as ps2-4-a-2.png), text response - description of how it compares to the SSD version and to the ground truth.
"""

print "part 4a"
DL = disparity_ncorr(L, R)
DR = disparity_ncorr(R, L)
write_disparity('output/ps2-4-a-1.png', DL)
write_disparity('output/ps2-4-a-2.png', DL)


"""
4.b
Now test it on both the noisy and contrast-boosted versions from 2-a and 2-b.
Output: Disparity images (Gaussian noise: DL as ps2-4-b-1.png and DR as ps2-4-b-2.png; contrast-boosted: DL as ps2-4-b-3.png and DR as ps2-4-b-4.png), text response - analysis of results comparing original to noise and contrast-boosted images.
"""

print "part 4b"
DL = disparity_ncorr(Lblurred, R)
DR = disparity_ncorr(R, Lblurred)
write_disparity('output/ps2-4-b-1.png', DL)
write_disparity('output/ps2-4-b-2.png', DL)

DL = disparity_ncorr(Lcontrast, R)
DR = disparity_ncorr(R, Lcontrast)
write_disparity('output/ps2-4-b-3.png', DL)
write_disparity('output/ps2-4-b-4.png', DL)

"""
5.a
Finally, there is a second pair of images: pair2-L.png and pair2-R.png
Try your algorithms on this pair.
Play with the images - smooth, sharpen, etc. Keep comparing to the ground truth (pair2-D_L.png and pair2-D_R.png).
Output: Disparity images  (DL as ps2-5-a-1.png and DR as ps2-5-a-2.png),
text response - analysis of what it takes to make stereo work using a window based approach.
"""

print "part 5a.1"
L = cv2.imread(os.path.join('input', 'pair2-L.png'), 0) * (1.0 / 255.0)  # grayscale, [0, 1]
R = cv2.imread(os.path.join('input', 'pair2-R.png'), 0) * (1.0 / 255.0)

DL = disparity_ssd(L, R)
DR = disparity_ssd(R, L)
write_disparity('output/ps2-5-a-1-base.png', DL)
write_disparity('output/ps2-5-a-2-base.png', DR)

print "part 5a.2"
Lblurred = cv2.GaussianBlur(L, (7, 7), 4)
Rblurred = cv2.GaussianBlur(L, (7, 7), 4)
DL = disparity_ssd(Lblurred, Rblurred)
DR = disparity_ssd(Rblurred, Lblurred)
write_disparity('output/ps2-5-a-1-blurred.png', DL)
write_disparity('output/ps2-5-a-2-blurred.png', DR)

print "part 5a.3"
Lsharp = 1.5 * L - 0.5 * Lblurred
Rsharp = 1.5 * R - 0.5 * Rblurred
cv2.imwrite('Lsharp.png', (Lsharp * 255).astype(np.uint8))
cv2.imwrite('Rsharp.png', (Rsharp * 255).astype(np.uint8))
DL = disparity_ssd(Lsharp, Rsharp)
DR = disparity_ssd(Rsharp, Lsharp)
write_disparity('output/ps2-5-a-1-sharp.png', DL)
write_disparity('output/ps2-5-a-2-sharp.png', DR)


# color channels
