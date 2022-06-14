# ----------
# User Instructions:
# 
# Create a function compute_value() which returns
# a grid of values. Value is defined as the minimum
# number of moves required to get from a cell to the
# goal. 
#
# If it is impossible to reach the goal from a cell
# you should assign that cell a value of 99.

# ----------

grid = [[0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0]]

init = [0, 0]
goal = [len(grid)-1, len(grid[0])-1]

delta = [[-1, 0 ], # go up
         [ 0, -1], # go left
         [ 1, 0 ], # go down
         [ 0, 1 ]] # go right

delta_name = ['^', '<', 'v', '>']

cost_step = 1 # the cost associated with moving from a cell to an adjacent one.

# ----------------------------------------
# insert code below
# ----------------------------------------

def optimum_policy():
    value = [[99 for row in range(len(grid[0]))] for col in range(len(grid))]
    policy = [[' ' for row in range(len(grid[0]))] for col in range(len(grid))]

    cost = 0
    value[goal[0]][goal[1]] = cost
    policy[goal[0]][goal[1]] = '*'
    open = []
    open.append([cost, goal[0], goal[1]])
    while len(open) > 0:
        (cost, x, y) = open.pop(0)
        cost += 1
        for i in range(len(delta)):
            d = delta[i]
            x2 = x - d[0]
            y2 = y - d[1]
            if x2 < 0 or y2 < 0 or x2 >= len(grid) or y2 >= len(grid[0]):
                continue

            if grid[x2][y2] == 1:
                continue

            if value[x2][y2] != 99:
                continue

            policy[x2][y2] = delta_name[i]
            value[x2][y2] = cost
            open.append([cost, x2, y2])

    for p in policy:
        print p

    return policy #make sure your function returns a grid of values as demonstrated in the previous video.

optimum_policy()


