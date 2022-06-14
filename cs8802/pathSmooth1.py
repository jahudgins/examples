# -----------
# User Instructions
#
# Define a function smooth that takes a path as its input
# (with optional parameters for weight_data, weight_smooth)
# and returns a smooth path.
#
# Smoothing should be implemented by iteratively updating
# each entry in newpath until some desired level of accuracy
# is reached. The update should be done according to the
# gradient descent equations given in the previous video:
#
# If your function isn't submitting it is possible that the
# runtime is too long. Try sacrificing accuracy for speed.
# -----------


from math import *

# Don't modify path inside your function.
path = [[0, 0],
        [0, 1],
        [0, 2],
        [1, 2],
        [2, 2],
        [3, 2],
        [4, 2],
        [4, 3],
        [4, 4]]

# ------------------------------------------------
# smooth coordinates
#

def smooth(path, weight_data = 0.5, weight_smooth = 0.1):

    # Make a deep copy of path into newpath
    newpath = [[0 for col in range(len(path[0]))] for row in range(len(path))]
    for i in range(len(path)):
        for j in range(len(path[0])):
            newpath[i][j] = path[i][j]


    #### ENTER CODE BELOW THIS LINE ###
    iterations = 0
    maxIterations = 2000
    tolerance = 0.0000001
    maxDelta = tolerance * 2
    while maxDelta > tolerance:
        maxDelta = 0
        for i in range(1, len(newpath)-1):
            for j in range(len(newpath[i])):
                oldValue = newpath[i][j]
                newpath[i][j] = newpath[i][j] + weight_data * (path[i][j] - newpath[i][j])
                newpath[i][j] = newpath[i][j] + weight_smooth * (newpath[i-1][j] + newpath[i+1][j] - 2 * newpath[i][j])
                maxDelta = max(maxDelta, abs(oldValue - newpath[i][j]))

        if iterations >= maxIterations:
            print "We hit max iterations: {0}".format(iterations)
            break
    
        iterations += 1
    
    return newpath # Leave this line for the grader!


def smooth2(path, weight_data = 0.5, weight_smooth = 0.1):

    # Make a deep copy of path into newpath
    newpath = [[0 for col in range(len(path[0]))] for row in range(len(path))]
    for i in range(len(path)):
        for j in range(len(path[0])):
            newpath[i][j] = path[i][j]


    #### ENTER CODE BELOW THIS LINE ###
    iterations = 0
    maxIterations = 2000
    tolerance = 0.0000001
    maxDelta = tolerance * 2
    while maxDelta > tolerance:
        datapath = []
        datapath.append(newpath[0])
        for i in range(1, len(newpath)-1):
            point = []
            for j in range(len(newpath[i])):
                point.append(newpath[i][j] + weight_data * (path[i][j] - newpath[i][j]))
            datapath.append(point)
        datapath.append(path[-1])

        smoothpath = []
        smoothpath.append(datapath[0])
        for i in range(1, len(datapath)-1):
            point = []
            for j in range(len(datapath[i])):
                point.append(datapath[i][j] + weight_smooth * (datapath[i-1][j] + datapath[i+1][j] - 2 * datapath[i][j]))
            smoothpath.append(point)
        smoothpath.append(path[-1])

        maxDelta = 0
        for i in range(len(path)):
            for j in range(len(newpath[i])):
                maxDelta = max(maxDelta, abs(newpath[i][j] - smoothpath[i][j]))
    
        newpath = smoothpath
        if iterations >= maxIterations:
            print "We hit max iterations: {0}".format(iterations)
            break
    
        iterations += 1
    
    return newpath # Leave this line for the grader!



# feel free to leave this and the following lines if you want to print.
newpath = smooth2(path)

# thank you - EnTerr - for posting this on our discussion forum
for i in range(len(path)):
    print '['+ ', '.join('%.3f'%x for x in path[i]) +'] -> ['+ ', '.join('%.3f'%x for x in newpath[i]) +']'


error = 0
for i in range(len(path)-1):
    for j in range(len(path[i])):
        error += 0.5 * (path[i][j] - newpath[i][j]) ** 2
        error += 0.1 * (path[i][j] - path[i+1][j]) ** 2
        error += 0.1 * (path[i][j] - path[i+1][j]) ** 2

print "Error: {0}".format(error)


