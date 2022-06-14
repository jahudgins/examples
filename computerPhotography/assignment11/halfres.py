# This script will split the target video file into frames in a subfolder
# under the same name.

import argparse
import cv2
import sys, os

if not os.path.exists(sys.argv[1]):
  print "Error - the given path is not valid: {}".format(sys.argv[1])

for filename in os.listdir(sys.argv[1]):
    path = os.path.join(sys.argv[1], filename)
    if os.path.isfile(path):
        image = cv2.imread(path)
        image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_LANCZOS4)
        cv2.imwrite(path, image)

