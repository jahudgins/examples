# ASSIGNMENT 8
# Jonathan Hudgins
# CS6475 Spring 2015 OMS
# GTID: 903050550

import argparse
import cv2
import numpy as np
import assignment8
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stich images together to form a panorama")
    parser.add_argument('--blendmode', choices=assignment8.blendmodes, default=assignment8.blendmodes[0])
    parser.add_argument('--outfile', required=True)
    parser.add_argument('source_file', nargs='+')
    args = parser.parse_args()

    print "Stitching images together:"
    print '\n'.join(args.source_file)
    pano = cv2.imread(args.source_file[0])
    for filename in args.source_file[1:]:
        image = cv2.imread(filename)
        pano_kp, image_kp, matches = assignment8.findMatchesBetweenImages(pano, image, 1000)

        homography = assignment8.findHomography(pano_kp, image_kp, matches)
        pano = assignment8.warpImagePair(pano, image, homography, args.blendmode)

        
    cv2.imwrite(args.outfile, pano)
