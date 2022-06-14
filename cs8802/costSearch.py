# ----------
# User Instructions:
# 
# Implement the function optimum_policy2D() below.
#
# You are given a car in a grid with initial state
# init = [x-position, y-position, orientation]
# where x/y-position is its position in a given
# grid and orientation is 0-3 corresponding to 'up',
# 'left', 'down' or 'right'.
#
# Your task is to compute and return the car's optimal
# path to the position specified in `goal'; where
# the costs for each motion are as defined in `cost'.

# EXAMPLE INPUT:

# grid format:
#     0 = navigable space
#     1 = occupied space 
grid = [[1, 1, 1, 0, 0, 0],
        [1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1, 1]]
goal = [2, 0] # final position
init = [4, 3, 0] # first 2 elements are coordinates, third is direction
cost = [2, 1, 20] # the cost field has 3 values: right turn, no turn, left turn

# EXAMPLE OUTPUT:
# calling optimum_policy2D() should return the array
# 
# [[' ', ' ', ' ', 'R', '#', 'R'],
#  [' ', ' ', ' ', '#', ' ', '#'],
#  ['*', '#', '#', '#', '#', 'R'],
#  [' ', ' ', ' ', '#', ' ', ' '],
#  [' ', ' ', ' ', '#', ' ', ' ']]
#
# ----------


# there are four motion directions: up/left/down/right
# increasing the index in this array corresponds to
# a left turn. Decreasing is is a right turn.

forward = [[-1,  0], # go up
           [ 0, -1], # go left
           [ 1,  0], # go down
           [ 0,  1]] # do right
forward_name = ['up', 'left', 'down', 'right']

# the cost field has 3 values: right turn, no turn, left turn
action = [-1, 0, 1]
action_name = ['R', '#', 'L']


# ----------------------------------------
# modify code below
# ----------------------------------------

import copy
import heapq

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def calcPolicy(path):
    policy = [[' ' for row in range(len(grid[0]))] for col in range(len(grid))]
    policy[goal[0]][goal[1]] = '*'
    for (x, y, a) in path:
        policy[x][y] = action_name[a]
    return policy

def optimum_policy2D():

    values = [[[999 for dir in range(len(forward))] for row in range(len(grid[0]))] for col in range(len(grid))]
    open = []

    # use manhattan for our heuristic
    c = 0
    f = c + manhattan(goal, init[0:2])

    # use a heap for a priority queue
    heapq.heappush(open, [f, c, init[0], init[1], init[2], []])
    while len(open) > 0:

        # get minium A*
        (f, c, x, y, direction, path) = heapq.heappop(open)

        for actionIndex in range(len(action)):
            # get action and new cost
            a = action[actionIndex]
            c2 = c + cost[actionIndex]

            # keep track of path
            path2 = copy.deepcopy(path)
            path2.append([x, y, actionIndex])

            # calc direction resulting from this action
            direction2 = (a + direction) % len(forward)

            # calc new position based on movement after action
            move = forward[direction2]
            x2 = x + move[0]
            y2 = y + move[1]

            # if at goal just return policy of the path that got us here
            if x2 == goal[0] and y2 == goal[1]:
                return calcPolicy(path2)

            if x2 < 0 or y2 < 0 or x2 >= len(grid) or y2 >= len(grid[0]):
                continue

            if grid[x2][y2] == 1:
                continue

            if c2 >= values[x2][y2][direction2]:
                continue

            values[x2][y2][direction2] = c2
            f2 = c2 + manhattan(goal, [x2, y2])
            heapq.heappush(open, [f2, c2, x2, y2, direction2, path2])

    return calcPolicy([]) # Make sure your function returns the expected grid.


policy = optimum_policy2D()
for p in policy:
    print p

