# ----------
# Part Two
#
# Now we'll make the scenario a bit more realistic. Now Traxbot's
# sensor measurements are a bit noisy (though its motions are still
# completetly noise-free and it still moves in an almost-circle).
# You'll have to write a function that takes as input the next
# noisy (x, y) sensor measurement and outputs the best guess 
# for the robot's next position.
#
# ----------
# YOUR JOB
#
# Complete the function estimate_next_pos. You will be considered 
# correct if your estimate is within 0.01 stepsizes of Traxbot's next
# true position. 
#
# ----------
# GRADING
# 
# We will make repeated calls to your estimate_next_pos function. After
# each call, we will compare your estimated position to the robot's true
# position. As soon as you are within 0.01 stepsizes of the true position,
# you will be marked correct and we will tell you how many steps it took
# before your function successfully located the target bot.

# These import steps give you access to libraries which you may (or may
# not) want to use.
from robot import *  # Check the robot.py tab to see how this works.
from math import *
from matrix import * # Check the matrix.py tab to see how this works.
import random

import sys

## Plotting ##
##############

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

def plotEstimate(x1, x2, color):
    if subplot:
        arrowLength = .5
        values1 = x1.transpose().value[0]
        values2 = x2.transpose().value[0]

        xx1 = values1[0]
        xy1 = values1[1]
        vx1 = values1[2]
        vy1 = values1[3]

        xx2 = values2[0]
        xy2 = values2[1]
        vx2 = values2[2]
        vy2 = values2[3]

        subplot.arrow(xx2, xy2, arrowLength * vx2, arrowLength * vy2, head_width=0.1, head_length=0.2, fc='k', ec='k')
        subplot.plot([xx1, xx2], [xy1, xy2], color=color)

 
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

# This is the function you have to write. The argument 'measurement' is a 
# single (x, y) point. This function will have to be called multiple
# times before you have enough information to accurately predict the
# next position. The OTHER variable that your function returns will be 
# passed back to your function the next time it is called. You can use
# this to keep track of important information over time.

def estimate_kalman(measurement, OTHER = None):
    """Estimate the next (x, y) position of the wandering Traxbot
    based on noisy (x, y) measurements."""

    lastMeasurement = None

    ## use Kalman filter to predict next based on previous measurement
    if not OTHER:
        # I tried 4, 6, 8, 10 dimensions -- 6 (modeling acceleration) converged too slowly
        # 8 and 10 become unstable after about 20 iterations, so take 8 (Occum's Razor)
        # 2 direction (x, y), 2 for x,y velcoity, 2 for x,y acceleration, 2 for x,y jerk-rate
        dim = 8

        ## x: initial state
        # Create x-matrix (dim x 1) setting the first two rows to x and y measurement
        x = matrix([[]])
        x.zero(dim, 1)
        x.value[0][0] = measurement[0]
        x.value[1][0] = measurement[1]

        ## P: initial uncertainty
        # Create P with high uncertainty in non-measured dimensions
        P = matrix([[]])
        P.zero(dim, dim)
        for i in range(2, dim):
            P.value[i][i] = 1000.

        ## F: Next State Function
        # Create F using x' = x + vt + at **2 / 2! + jt **3 / 3! + ...
        #
        # http://en.wikipedia.org/wiki/Jerk_(physics)
        #
        # So the first row of the matrix (just x-dimension) [1, dt, dt**2/2, dt**3/6]
        #
        F = matrix([[]])
        F.identity(dim)

        dt = 1.0
        fdim = dim
        factor = 1.0 * dt
        count = 0
        while fdim > 2:
            for i in range(0, fdim-2, 2):
                F.value[i][i+2+count*2] = factor
                F.value[i+1][i+3+count*2] = factor
            count += 1
            factor = factor * dt / (count + 1)
            fdim -= 2

        
        ## H: measurement function
        H = matrix([[]])
        H.zero(2, dim)
        H.value[0][0] = 1.0
        H.value[1][1] = 1.0

        ## R: measurement uncertainty
        R = matrix([[ measurement_noise, 0.],
                    [ 0., measurement_noise]])

        kalmanFilter = KalmanFilter(x, P, F, H, R)
        OTHER = [measurement, kalmanFilter]

    else:
        # get values from OTHER
        lastMeasurement, kalmanFilter = OTHER
        OTHER[0] = measurement
        lastX = kalmanFilter.x

        # call measure
        kalmanFilter.measure(measurement)

    # call predict
    kalmanFilter.predict()

    # After about 20 iterations, jerk rate uncertainty becomes so small that
    # jerk rate dominates. Acceleration is also small enough to cause problems,
    # but if I force our jerk uncertainty to remain above a minimum, the acceleration
    # will adjust as necessary. In fact, I simply provide a max for the highest dimension
    # (in case we want to try higher dimensions)
    #
    # There is probably a more elegant way (theoretically) of doing this, but this
    # is simple and gives us great results.
    #
    kalmanFilter.P.value[-2][-2] = max(kalmanFilter.P.value[-2][-2], 0.05)
    kalmanFilter.P.value[-1][-1] = max(kalmanFilter.P.value[-1][-1], 0.05)
    
    if lastMeasurement:
        # plot so we can see what is going on
        plotPath([lastMeasurement, measurement], 'green')
        plotEstimate(lastX, kalmanFilter.x, 'red')

    xy_estimate = [kalmanFilter.x.value[0][0], kalmanFilter.x.value[1][0]]

    # You must return xy_estimate (x, y), and OTHER (even if it is None) 
    # in this order for grading purposes.
    return xy_estimate, OTHER

def vectorSub(a, b):
    return [a[0] - b[0], a[1] - b[1]]

def vectorLength(a):
    return sqrt(a[0] ** 2 + a[1] ** 2)

def estimate_discrete(measurement, OTHER = None):
    if not OTHER:
        OTHER = [[[measurement[0], measurement[1]]], []]
        xy_estimate = [measurement[0], measurement[1]]
        last_estimate = xy_estimate
    else:
        measurements, last_estimate = OTHER
        measurements.append([measurement[0], measurement[1]])
        plotPath([measurements[-2], measurements[-1]], 'green')
        if len(measurements) == 3:
            # calculate path segments
            segment1 = vectorSub(measurements[1], measurements[0])
            segment2 = vectorSub(measurements[2], measurements[1])
            dist = vectorLength(segment1)

            # calculate angles
            angle1 = atan2(segment1[1], segment1[0])
            angle2 = atan2(segment2[1], segment2[0])
            angle3 = angle2 + (angle2 - angle1)

            # calculate prediction
            xy_estimate = [measurement[0] + dist * cos(angle3), measurement[1] + dist * sin(angle3)] 

            # remove the oldest measurement
            measurements.pop(0)

        else:
            # we could improve this by extrapolating a straight line, but that's not necessary, since
            # next step we will get a more accurate model
            xy_estimate = [measurement[0], measurement[1]]

    plotPath([last_estimate, xy_estimate], 'red')

    OTHER[1] = xy_estimate
    return xy_estimate, OTHER

def estimate_kalmanAngular(measurement, OTHER = None):
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

        plotPath([measurements[-2], measurements[-1]], 'green')
        plotPoint(measurement, 'blue')

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

    plotPath([last_estimate, xy_estimate], 'red')

    OTHER['measurements'] = measurements
    OTHER['last_estimate'] = xy_estimate
    OTHER['kalmanFilter'] = kalmanFilter
    OTHER['last_heading'] = heading

    return xy_estimate, OTHER



def estimate_next_pos(measurement, OTHER = None):
    return estimate_kalmanAngular(measurement, OTHER)
    # return estimate_kalman(measurement, OTHER)
    # return estimate_discrete(measurement, OTHER)

# A helper function you may find useful.
def distance_between(point1, point2):
    """Computes distance between point1 and point2. Points are (x, y) pairs."""
    x1, y1 = point1
    x2, y2 = point2
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# This is here to give you a sense for how we will be running and grading
# your code. Note that the OTHER variable allows you to store any 
# information that you want. 
def demo_grading(estimate_next_pos_fcn, target_bot, OTHER = None):
    localized = False
    distance_tolerance = 0.01 * target_bot.distance
    ctr = 0
    # if you haven't localized the target bot, make a guess about the next
    # position, then we move the bot and compare your guess to the true
    # next position. When you are close enough, we stop checking.
    iterations = 2000
    while not localized and ctr <= iterations:
        ctr += 1
        measurement = target_bot.sense()
        position_guess, OTHER = estimate_next_pos_fcn(measurement, OTHER)
        target_bot.move_in_circle()
        true_position = (target_bot.x, target_bot.y)
        error = distance_between(position_guess, true_position)
        # print "Error: {:.3f}".format(error)
        if error <= distance_tolerance:
            print "You got it right! It took you ", ctr, " steps to localize."
            localized = True
        if ctr == iterations:
            print "Sorry, it took you too many steps to localize the target."
    return localized

# This is a demo for what a strategy could look like. This one isn't very good.
def naive_next_pos(measurement, OTHER = None):
    """This strategy records the first reported position of the target and
    assumes that eventually the target bot will eventually return to that 
    position, so it always guesses that the first position will be the next."""
    if not OTHER: # this is the first measurement
        OTHER = measurement
    xy_estimate = OTHER 
    return xy_estimate, OTHER

# This is how we create a target bot. Check the robot.py file to understand
# How the robot class behaves.
test_target = robot(2.1, 4.3, 0.5, 2*pi / 34.0, 1.5)
measurement_noise = 0.05 * test_target.distance
test_target.set_noise(0.0, 0.0, measurement_noise)

# demo_grading(naive_next_pos, test_target)
demo_grading(estimate_next_pos, test_target)


turning = 2*pi/50
while turning < 2*pi/4:
    test_target = robot(turning = turning)
    test_target.set_noise(0.0, 0.0, new_m_noise = 0.05 * test_target.distance)
    if not demo_grading(estimate_next_pos, test_target):
        print "Robot fails for turning = {0}".format(turning)
        break
    turning += 2*pi /25

if subplot:
    plt.axis('equal')
    plt.show()

