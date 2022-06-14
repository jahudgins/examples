# ----------
# Part Four
#
# Again, you'll track down and recover the runaway Traxbot. 
# But this time, your speed will be about the same as the runaway bot. 
# This may require more careful planning than you used last time.
#
# ----------
# YOUR JOB
#
# Complete the next_move function, similar to how you did last time. 
#
# ----------
# GRADING
# 
# Same as part 3. Again, try to catch the target in as few steps as possible.

from robot import *
from math import *
from matrix import *
import random

subplot = None
plotting = False
if plotting:
    try:
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        fig = plt.figure()
        subplot = fig.add_subplot(111)
    except ImportError, e:
        print "No plotting because: {0}".format(e)
        print "  Windows: try downloading from http://www.lfd.uci.edu/~gohlke/pythonlibs/#matplotlib"
        print "  Linux: use 'sudo apt-get install python-matplotlib'"

def plotPoint(point, color):
    if subplot:
        subplot.plot(point[0], point[1], color=color, marker='+')

def plotPath(path, color):
    if subplot:
        subplot.plot([a for a,b in path], [b for a,b in path], color=color)
        subplot.plot(path[0][0], path[0][1], color=color, marker='o')

def vectorSub(a, b):
    return [a[0] - b[0], a[1] - b[1]]

def vectorLength(a):
    return sqrt(a[0] ** 2 + a[1] ** 2)

## Kalman Filter Class ##
#########################

class KalmanFilter:
    def __init__(self, x, P, F, H, R):
        self.x = x # initial state
        self.P = P # initial uncertainty
        self.F = F # next state function
        self.H = H # measurement function
        self.R = R # measurement uncertainty

        # set identity matrix
        if self.R.dimx != self.R.dimy:
            raise ValueError, "R needs to be a square matrix (dimx={0}, dimy={1})".format(self.R.dimx, self.R.dimy)
        self.I = matrix([[]])
        self.I.identity(self.P.dimx)

    def measure(self, measurement):
        # measurement update
        Z = matrix([measurement])
        y = Z.transpose() - (self.H * self.x)
        S = self.H * self.P * self.H.transpose() + self.R
        K = self.P * self.H.transpose() * S.inverse()
        self.x = self.x + (K * y)
        self.P = (self.I - (K * self.H)) * self.P

    def predict(self):
        self.x = self.F * self.x
        # add external motion 'u' here if needed
        # x += u
        self.P = self.F * self.P * self.F.transpose()

def estimate_kalmanAngular(measurement, OTHER = None, plot=True):
    if not OTHER:
        OTHER = {}
        xy_estimate = [measurement[0], measurement[1]]
        measurements = [xy_estimate]
        last_estimate = xy_estimate
        kalmanFilter = None
        heading = 0.0
    else:
        measurements = OTHER['measurements']
        last_estimate = OTHER['last_estimate']
        kalmanFilter = OTHER['kalmanFilter']
        last_heading = OTHER['last_heading']

        measurements.append([measurement[0], measurement[1]])

        if plot:
            plotPath([measurements[-2], measurements[-1]], 'green')
        # plotPoint(measurement, 'blue')

        if len(measurements) == 2:
            # calculate path segments
            segment = vectorSub(measurements[1], measurements[0])
            dist = vectorLength(segment)

            # calculate heading
            heading = atan2(segment[1], segment[0])

            # adjust heading to be in the same phase as the last_heading
            while heading < last_heading - pi:
                heading += 2 * pi
            while heading > last_heading + pi:
                heading -= 2 * pi


            # now enter our distance and angle into a simple kalman filter
            if kalmanFilter:
                kalmanFilter.measure([dist, heading])
            else:

                ## initialize kalman filter
                dim = 4

                ## x: initial state
                # Create x-matrix (dim x 1) setting the first two rows to dist and angle measurements
                x = matrix([[]])
                x.zero(dim, 1)
                x.value[0][0] = dist
                x.value[1][0] = heading

                ## P: initial uncertainty
                # Create P with high uncertainty in non-measured dimensions
                P = matrix([[]])
                P.zero(dim, dim)
                for i in range(2, dim):
                    P.value[i][i] = 1000.

                ## F: Next State Function
                #
                F = matrix([[1.0, 0.0, 1.0, 0.0],
                            [0.0, 1.0, 0.0, 1.0],
                            [0.0, 0.0, 1.0, 0.0],
                            [0.0, 0.0, 0.0, 1.0]])
                
                ## H: measurement function
                H = matrix([[]])
                H.zero(2, dim)
                H.value[0][0] = 1.0
                H.value[1][1] = 1.0

                ## R: measurement uncertainty
                R = matrix([[ 0.1, 0.],
                            [ 0., 0.1]])

                kalmanFilter = KalmanFilter(x, P, F, H, R)

            kalmanFilter.predict()
            dist = kalmanFilter.x.value[0][0]
            heading = kalmanFilter.x.value[1][0]

            # calculate prediction
            xy_estimate = [measurement[0] + dist * cos(heading), measurement[1] + dist * sin(heading)] 

            # remove the oldest measurement
            measurements.pop(0)

        else:
            # we could improve this by extrapolating a straight line, but that's not necessary, since
            # next step we will get a more accurate model
            xy_estimate = [measurement[0], measurement[1]]

    #if plot:
    #    plotPath([last_estimate, xy_estimate], 'red')

    OTHER['measurements'] = measurements
    OTHER['last_estimate'] = xy_estimate
    OTHER['kalmanFilter'] = kalmanFilter
    OTHER['last_heading'] = heading

    return xy_estimate, OTHER

def estimate_next_pos(measurement, OTHER = None, plot=True):
    return estimate_kalmanAngular(measurement, OTHER, plot)

import copy

def next_move(hunter_position, hunter_heading, target_measurement, max_distance, OTHER = None):
    # This function will be called after each time the target moves. 

    target_next, OTHER = estimate_next_pos(target_measurement, OTHER)

    hunter_to_target_dist = distance_between(target_next, hunter_position)

    # if I can't reach target_next, predict the second step and try to go there
    if hunter_to_target_dist > max_distance:
        nextOther = copy.deepcopy(OTHER)
        target_next, nextOther = estimate_next_pos(target_next, nextOther, plot=False)
        hunter_to_target_dist = distance_between(target_next, hunter_position)

        # if I can't the second step, try to go to the third step (I think this will converge
        # to the target's path and I can hit the target head-on instead of behind)
        if hunter_to_target_dist > max_distance:
            target_next, nextOther = estimate_next_pos(target_next, nextOther, plot=False)
    
    next_heading = get_heading(hunter_position, target_next)
    turning = next_heading - hunter_heading
    distance = min(max_distance, distance_between(target_next, hunter_position))

    next_pos = [distance * cos(next_heading) + hunter_position[0], distance * sin(next_heading) + hunter_position[1]]
    plotPath([hunter_position, next_pos], 'blue')

    # predict where I can best hit the target
        # t * target_vector + target_measurement = point
        # t * max_distance * [sin(heading), cos(heading)] + hunter_position = point


    # The OTHER variable is a place for you to store any historical information about
    # the progress of the hunt (or maybe some localization information). Your return format
    # must be as follows in order to be graded properly.
    return turning, distance, OTHER

def distance_between(point1, point2):
    """Computes distance between point1 and point2. Points are (x, y) pairs."""
    x1, y1 = point1
    x2, y2 = point2
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def demo_grading(hunter_bot, target_bot, next_move_fcn, OTHER = None):
    """Returns True if your next_move_fcn successfully guides the hunter_bot
    to the target_bot. This function is here to help you understand how we 
    will grade your submission."""
    max_distance = 0.98 * target_bot.distance # 1.94 is an example. It will change.
    separation_tolerance = 0.02 * target_bot.distance # hunter must be within 0.02 step size to catch target
    caught = False
    ctr = 0

    # We will use your next_move_fcn until we catch the target or time expires.
    iterations = 1000
    while not caught and ctr < iterations:

        # Check to see if the hunter has caught the target.
        hunter_position = (hunter_bot.x, hunter_bot.y)
        target_position = (target_bot.x, target_bot.y)
        separation = distance_between(hunter_position, target_position)
        if separation < separation_tolerance:
            print "You got it right! It took you ", ctr, " steps to catch the target."
            caught = True

        # The target broadcasts its noisy measurement
        target_measurement = target_bot.sense()

        # This is where YOUR function will be called.
        turning, distance, OTHER = next_move_fcn(hunter_position, hunter_bot.heading, target_measurement, max_distance, OTHER)
        
        # Don't try to move faster than allowed!
        if distance > max_distance:
            distance = max_distance

        # We move the hunter according to your instructions
        hunter_bot.move(turning, distance)

        # The target continues its (nearly) circular motion.
        target_bot.move_in_circle()

        ctr += 1            
        if ctr >= iterations:
            print "It took too many steps to catch the target."
    return caught



def angle_trunc(a):
    """This maps all angles to a domain of [-pi, pi]"""
    while a < 0.0:
        a += pi * 2
    return ((a + pi) % (pi * 2)) - pi

def get_heading(hunter_position, target_position):
    """Returns the angle, in radians, between the target and hunter positions"""
    hunter_x, hunter_y = hunter_position
    target_x, target_y = target_position
    heading = atan2(target_y - hunter_y, target_x - hunter_x)
    heading = angle_trunc(heading)
    return heading

def naive_next_move(hunter_position, hunter_heading, target_measurement, max_distance, OTHER):
    """This strategy always tries to steer the hunter directly towards where the target last
    said it was and then moves forwards at full speed. This strategy also keeps track of all 
    the target measurements, hunter positions, and hunter headings over time, but it doesn't 
    do anything with that information."""
    if not OTHER: # first time calling this function, set up my OTHER variables.
        measurements = [target_measurement]
        hunter_positions = [hunter_position]
        hunter_headings = [hunter_heading]
        OTHER = (measurements, hunter_positions, hunter_headings) # now I can keep track of history
    else: # not the first time, update my history
        OTHER[0].append(target_measurement)
        OTHER[1].append(hunter_position)
        OTHER[2].append(hunter_heading)
        measurements, hunter_positions, hunter_headings = OTHER # now I can always refer to these variables
    
    heading_to_target = get_heading(hunter_position, target_measurement)
    heading_difference = heading_to_target - hunter_heading
    turning =  heading_difference # turn towards the target
    distance = max_distance # full speed ahead!
    return turning, distance, OTHER

target = robot(0.0, 10.0, 0.0, 2*pi / 30, 1.5)
# measurement_noise = .05*target.distance
# target.set_noise(0.0, 0.0, measurement_noise)

hunter = robot(-10.0, -10.0, 0.0)

#print demo_grading(hunter, target, naive_next_move)
print demo_grading(hunter, target, next_move)


if subplot:
    plt.axis('equal')
    plt.show()

