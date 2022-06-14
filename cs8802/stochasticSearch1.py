# --------------
# USER INSTRUCTIONS
#
# Write a function called stochastic_value that 
# takes no input and RETURNS two grids. The
# first grid, value, should contain the computed
# value of each cell as shown in the video. The
# second grid, policy, should contain the optimum
# policy for each cell.
#
# Stay tuned for a homework help video! This should
# be available by Thursday and will be visible
# in the course content tab.
#
# Good luck! Keep learning!
#
# --------------
# GRADING NOTES
#
# We will be calling your stochastic_value function
# with several different grids and different values
# of success_prob, collision_cost, and cost_step.
# In order to be marked correct, your function must
# RETURN (it does not have to print) two grids,
# value and policy.
#
# When grading your value grid, we will compare the
# value of each cell with the true value according
# to this model. If your answer for each cell
# is sufficiently close to the correct answer
# (within 0.001), you will be marked as correct.
#
# NOTE: Please do not modify the values of grid,
# success_prob, collision_cost, or cost_step inside
# your function. Doing so could result in your
# submission being inappropriately marked as incorrect.

# -------------
# GLOBAL VARIABLES
#
# You may modify these variables for testing
# purposes, but you should only modify them here.
# Do NOT modify them inside your stochastic_value
# function.

grid = [[0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 1, 1, 0]]
       
goal = [0, len(grid[0])-1] # Goal is in top right corner


delta = [[-1, 0 ], # go up
         [ 0, -1], # go left
         [ 1, 0 ], # go down
         [ 0, 1 ]] # go right

delta_name = ['^', '<', 'v', '>'] # Use these when creating your policy grid.

success_prob = 0.5                      
failure_prob = (1.0 - success_prob)/2.0 # Probability(stepping left) = prob(stepping right) = failure_prob
collision_cost = 100                    
cost_step = 1        
                     

############## INSERT/MODIFY YOUR CODE BELOW ##################
#
# You may modify the code below if you want, but remember that
# your function must...
#
# 1) ...be called stochastic_value().
# 2) ...NOT take any arguments.
# 3) ...return two grids: FIRST value and THEN policy.

import heapq

def collision(x2, y2):
    if x2 < 0 or y2 < 0 or x2 >= len(grid) or y2 >= len(grid[0]):
        return 1

    if grid[x2][y2] == 1:
        return 1

    return 0


def costFailure(x2, y2, direction):
    x2 += delta[direction][0]
    y2 += delta[direction][1]
    return collision_cost * collision(x2, y2)
    

def stochastic_value():
    value = [[1000 for row in range(len(grid[0]))] for col in range(len(grid))]
    policy = [[' ' for row in range(len(grid[0]))] for col in range(len(grid))]
    

    cost = 0
    value[goal[0]][goal[1]] = cost
    policy[goal[0]][goal[1]] = '*'
    open = []
    heapq.heappush(open, [cost, goal[0], goal[1]])
    while len(open) > 0:
        (cost, x, y) = heapq.heappop(open)
        cost += 1
        for i in range(len(delta)):
            d = delta[i]
            x2 = x - d[0]
            y2 = y - d[1]

            if collision(x2, y2):
                continue

            cost2 = cost
            cost2 += failure_prob * costFailure(x2, y2, (i-1) % len(delta))
            cost2 += failure_prob * costFailure(x2, y2, (i+1) % len(delta))
            cost2 += success_prob * value[x][y]

            if cost2 >= value[x2][y2]:
                continue

            policy[x2][y2] = delta_name[i]
            value[x2][y2] = cost2
            heapq.heappush(open, [cost2, x2, y2])

    print "policy"
    for p in policy:
        print p
    print

    print "value"
    for v in value:
        print v
    print

    return value, policy


stochastic_value()
