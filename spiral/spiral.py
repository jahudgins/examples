import cv2
import numpy as np
import math


# https://en.wikipedia.org/wiki/Golden_spiral
phi = (1 + math.sqrt(2)) / 2
golden_spiral_base = math.pow(phi, 2 / math.pi)
repeat = 2
reverse = True
lerp_percent = 0.1

def convert_xy(u, v, width, height):
    x = u - width / 2
    y = v - height / 2
    return x, y

def calc_spiral_value(x, y):
    radius = math.sqrt(x * x + y * y)
    theta = math.atan2(y, x)
    if reverse:
        theta = -theta
    if radius == 0:
        return 0
    base_theta_at_radius = math.log(radius, golden_spiral_base)
    theta_delta = theta - base_theta_at_radius
    theta_offset = theta_delta / (2 * math.pi / repeat)
    theta_fraction = theta_offset - int(theta_offset)
    if theta_offset < 0:
        theta_fraction += 1
    black_to_white_lerp = 2 * abs(theta_fraction - 0.5)
    black_to_white_aa = (black_to_white_lerp - (0.5 - lerp_percent/2)) / lerp_percent
    #print(f'{theta_fraction=}, {black_to_white_lerp=}, {black_to_white_aa=}')
    return 255 * max(0, min(1, black_to_white_aa))
    #return min(250, 255 *
    #if theta_fraction <= 0.5:
    #    return 255
    #else:
    #    return 0

def main():
    height = 1024 * 3
    width = 1024 * 3
    spiral_image = np.zeros((height, width), dtype=np.uint8)
    for v in range(height):
        for u in range(width):
            x, y = convert_xy(u, v, width, height)
            spiral_image[v][u] = calc_spiral_value(x, y)
    filebase = f'spiral_{repeat}'
    if reverse:
        filebase += '_reverse'
    cv2.imwrite(f'{filebase}.png', spiral_image)
    dim = (1024, 1024)
    downsampled = cv2.resize(spiral_image, dim, interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(f'downsampled_{filebase}.png', spiral_image)
    # cv2.imshow('input1.png', resized1)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
