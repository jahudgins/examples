import numpy as np
import math
import sys

def hough_lines_acc(BW, RhoResolution=1.0, Theta=np.arange(-90., 90.)):
 # % Compute Hough accumulator array for finding lines.
    # %
    # % BW: Binary (black and white) image containing edge pixels
    # % RhoResolution (optional): Difference between successive rho values, in pixels
    # % Theta (optional): Vector of theta values to use, in degrees
    # %
    # % Please see the Matlab documentation for hough():
    # % http://www.mathworks.com/help/images/ref/hough.html
    # % Your code should imitate the Matlab implementation.
    # %
    # % Pay close attention to the coordinate system specified in the assignment.
    # % Note: Rows of H should correspond to values of rho, columns those of theta.
    # %% Parse input arguments
#     p = inputParser();
#     p = p.addParamValue('RhoResolution', 1);
#     p = p.addParamValue('Theta', linspace(-90, 89, 180));
#     p = p.parse(varargin{:});
# 
#     rhoStep = p.Results.RhoResolution;
#     Theta = p.Results.Theta;
    # %% TODO: Your code here

    max_rho = np.linalg.norm(BW.shape)
    rho = np.arange(-max_rho, max_rho, RhoResolution)
    H = np.zeros((len(rho), len(Theta)))

    edge_coords = BW.nonzero()
    i = 0
    sys.stdout.write("{} edge coords:".format(len(edge_coords[0])))
    sys.stdout.flush()
    progress_mod = len(edge_coords[0]) / 20
    progress = 0
    while i < len(edge_coords[0]):
        if (i+1) % progress_mod == 0:
            progress += 100/20
            sys.stdout.write("{}% ".format(progress))
            sys.stdout.flush()
        y = edge_coords[0][i]
        x = edge_coords[1][i]
        i += 1
        tIndex = 0
        for t in Theta:
            radians = t * math.pi / 180
            r = x * math.cos(radians) + y * math.sin(radians)
            rIndex = int((r + max_rho) / RhoResolution + 0.5)
            H[rIndex, tIndex] += 1

            """
            # code for keeping track of the endpoints
            # not super useful though because the length includes
            # outliers that aren't really part of the line
            if endpoint_dict!=None:
                key = (rIndex, tIndex)
                value = (y,x)
                if not endpoint_dict.has_key(key):
                    endpoint_dict[key] = [value, value, value, value]
                else:
                    p = endpoint_dict[key]
                    if value[0] < p[0][0]:
                        p[0] = value
                    elif value[0] > p[1][0]:
                        p[1] = value

                    if value[1] < p[2][1]:
                        p[2] = value
                    elif value[1] > p[3][1]:
                        p[3] = value
            """

            tIndex += 1


    sys.stdout.write("\n")
    return H, Theta, rho
