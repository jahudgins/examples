# ----------
# Part Five
#
# This time, the sensor measurements from the runaway Traxbot will be VERY 
# noisy (about twice the target's stepsize). You will use this noisy stream
# of measurements to localize and catch the target.
#
# ----------
# YOUR JOB
#
# Complete the next_move function, similar to how you did last time. 
#
# ----------
# GRADING
# 
# Same as part 3 and 4. Again, try to catch the target in as few steps as possible.

from robot import *
from math import *
from matrix import *
import random

subplot = None
plotting = True
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

def plotPoint(point, color, marker='+'):
    if subplot:
        subplot.plot(point[0], point[1], color=color, marker=marker)

def plotPath(path, color):
    if subplot:
        subplot.plot([a for a,b in path], [b for a,b in path], color=color)
        subplot.plot(path[0][0], path[0][1], color=color, marker='o')

def vectorSub(a, b):
    return [a[0] - b[0], a[1] - b[1]]

def vectorLength(a):
    return sqrt(a[0] ** 2 + a[1] ** 2)

def calculate_center(samples):
    center = [0., 0.]
    for sample in samples:
        center[0] += sample[0]
        center[1] += sample[1]
    center[0] /= len(samples)
    center[1] /= len(samples)
    return center

def calculate_radius(center, samples, angleDelta):
    # Because we are turning and the measurement noise will be uniform in every direction
    # the samples will be skewed outward from the center of the circle.
    # I think the ratio will be corresponding to the angle delta

    radius = 0.
    for sample in samples:
        radius += distance_between(center, sample)
    radius /= len(samples)
    radius *= (pi - angleDelta) / pi
    return radius

def calculate_angleDelta(center, samples):
    center = [-0.7500000000000007, 17.13577334066694]
    angleDelta = 0.
    lastAngle = get_heading(center, samples[0])
    for i in range(1, len(samples)):
        angle = get_heading(center, samples[i])
        angle = rephase_angle(angle, lastAngle)
        angleDelta += angle_trunc(angle - lastAngle)
        lastAngle = angle
    angleDelta /= (len(samples) - 1)
    return angleDelta

def rephase_angle(angle, last_angle):
    while angle < last_angle - pi:
        angle += 2 * pi
    while angle > last_angle + pi:
        angle -= 2 * pi
    return angle

def calculate_angleBase(center, angleDelta, samples):
    angleBase = 0.
    lastAngle = 0.
    for i in range(len(samples)):
        angle = angle_trunc(get_heading(samples[0], center))
        angle = rephase_angle(angle, lastAngle)
        lastAngle = angle
        angleBase += angle - i * angleDelta
    angleBase /= len(samples)
    return angleBase

def next_move(hunter_position, hunter_heading, target_measurement, max_distance, OTHER = None):
    minSamples = 920
    # minSamples = 30

    if not OTHER:
        OTHER = { 'samples':[], 'requiredSamples':0 }

    samples = OTHER['samples']
    requiredSamples = OTHER['requiredSamples']

    # less than minSamples ->  append target_measurement, just use average target position
    if len(samples)+1 < minSamples or requiredSamples > 0 and len(samples)+1 < requiredSamples:
        samples.append(target_measurement)
        target_next = calculate_center(samples)
    
    # otherwise, we will calculate target_next
    else:
        # calculate our model
        if len(samples)+1 == minSamples or len(samples)+1 == requiredSamples:

            #import pdb
            #pdb.set_trace()

            samples.append(target_measurement)
            center = calculate_center(samples)
            angleDelta = calculate_angleDelta(center, samples)
            angleBase = calculate_angleBase(center, angleDelta, samples)
            radius = calculate_radius(center, samples, angleDelta)
            time = len(samples)
            print "center=({0}, {1}), radius={2}, angleDelta={3}, angleBase={4}".format(center[0], center[1], radius, angleDelta, angleBase)

            # we want to avoid lopsided samples -- that is, we want to stop on complete circles
            if requiredSamples == 0:
                # calculate loops: round up and make sure we make at least one loop
                loops = max(int(minSamples * angleDelta / (2*pi) + 0.5), 1)

                # caclulate number of samples to make this many loops
                requiredSamples = int(loops * 2 * pi / angleDelta)
                OTHER['requiredSamples'] = requiredSamples
                
        else:
            center = OTHER['center']
            radius = OTHER['radius']
            angleDelta = OTHER['angleDelta']
            angleBase = OTHER['angleBase']
            time = OTHER['time'] + 1

        # update variables (not really needed for center, radius, angles -- but nice to have it in one spot)
        OTHER['center'] = center
        OTHER['radius'] = radius
        OTHER['angleDelta'] = angleDelta
        OTHER['angleBase'] = angleBase
        OTHER['time'] = time

        # now calculate the predicted location using angle based on time for the next step
        angle = angleBase + (time + 1) * angleDelta
        target_next = [center[0] + radius * cos(angle), center[1] + radius * sin(angle)]

        # if I can't reach target_next this frame, predict the second step and try to go there
        hunter_to_target_dist = distance_between(target_next, hunter_position)
        if hunter_to_target_dist > max_distance:
            angle = angleBase + (time + 2) * angleDelta
            target_next = [center[0] + radius * cos(angle), center[1] + radius * sin(angle)]

            # if I can't reach the second step this frame, try to go to the third step, then
            # I can hit the target head-on instead of from behind
            hunter_to_target_dist = distance_between(target_next, hunter_position)
            if hunter_to_target_dist > max_distance:
                angle = angleBase + (time + 3) * angleDelta
                target_next = [center[0] + radius * cos(angle), center[1] + radius * sin(angle)]


    # calclulate next heading, how much to turn to get there and distance to desired location
    next_heading = get_heading(hunter_position, target_next)
    turning = next_heading - hunter_heading
    distance = min(max_distance, distance_between(target_next, hunter_position))

    next_pos = [distance * cos(next_heading) + hunter_position[0], distance * sin(next_heading) + hunter_position[1]]
    plotPath([hunter_position, next_pos], 'blue')

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
    max_distance = 0.97 * target_bot.distance # 0.97 is an example. It will change.
    separation_tolerance = 0.02 * target_bot.distance # hunter must be within 0.02 step size to catch target
    caught = False
    ctr = 0

    last_pos = [target_bot.x, target_bot.y]
    # We will use your next_move_fcn until we catch the target or time expires.
    iterations = 1000
    while not caught and ctr < iterations:

        next_pos = [target_bot.x, target_bot.y]
        plotPath([last_pos, next_pos], 'red')
        last_pos = next_pos

        # Check to see if the hunter has caught the target.
        hunter_position = (hunter_bot.x, hunter_bot.y)
        target_position = (target_bot.x, target_bot.y)
        separation = distance_between(hunter_position, target_position)
        if separation < separation_tolerance:
            print "You got it right! It took you ", ctr, " steps to catch the target."
            caught = True

        # The target broadcasts its noisy measurement
        target_measurement = target_bot.sense()

        plotPoint(target_measurement, 'green')

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
measurement_noise = 2.0*target.distance # VERY NOISY!!
target.set_noise(0.0, 0.0, measurement_noise)

hunter = robot(-10.0, -10.0, 0.0)

def robotCenter(robot):
    # calculate alpha angle between next movement vector and position-to-center vector
    alpha = (pi - robot.turning) / 2.0

    # calculate radius
    radius = robot.distance / 2.0 / cos(alpha)

    # abosolute angle of position-to-center vector
    alpha_heading = robot.heading + robot.turning + alpha

    # calculate center 
    center = [robot.x + radius * cos(alpha_heading), robot.y + radius * sin(alpha_heading)]

    return center

center = robotCenter(target)
radius = distance_between(center, [target.x, target.y])
angleBase = get_heading(center, [target.x, target.y])
print center, radius, target.turning, angleBase

if subplot:
    plotPath([center, [target.x, target.y]], 'orange')

# print demo_grading(hunter, target, naive_next_move)


print demo_grading(hunter, target, next_move)
if subplot:
    center = robotCenter(target)
    #plotPoint(center, 'orange', marker='x'):
    plotPath([center, [target.x, target.y]], 'orange')
    plt.axis('equal')
    plt.show()


