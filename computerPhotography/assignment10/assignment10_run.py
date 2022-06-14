import sys
import os
import numpy as np
import cv2

import assignment10


if __name__ == "__main__":
    image_dir = "willrogers_tiny"
    output_dir = "output"
    exposure_times = np.float64([1/120., 1/95., 1/75., 1/60., 1/50., 1/40., 1/32., 1/25., 1/20.])
    log_exposure_times = np.log(exposure_times)

    np.random.seed()
    hdr = assignment10.computeHDR(image_dir, log_exposure_times)
    cv2.imwrite(output_dir + "/willrogers_hdr.jpg", hdr)

    image_dir = "willrogers_3"
    output_dir = "output"
    exposure_times = np.float64([1/120., 1/60., 1/30.])
    log_exposure_times = np.log(exposure_times)

    np.random.seed()
    hdr = assignment10.computeHDR(image_dir, log_exposure_times)
    cv2.imwrite(output_dir + "/willrogers_3_hdr.jpg", hdr)

