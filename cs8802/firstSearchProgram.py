# ----------
# User Instructions:
# 
# Define a function, search() that takes no input
# and returns a list
# in the form of [optimal path length, x, y]. For
# the grid shown below, your function should output
# [11, 4, 5].
#
# If there is no valid path from the start point
# to the goal, your function should return the string
# 'fail'
# ----------

# Grid format:
#   0 = Navigable space
#   1 = Occupied space

grid = [[0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 1, 0]]

init = [0, 0]
goal = [len(grid)-1, len(grid[0])-1] # Make sure that the goal definition stays in the function.

delta = [[-1, 0 ], # go up
        [ 0, -1], # go left
        [ 1, 0 ], # go down
        [ 0, 1 ]] # go right

delta_name = ['^', '<', 'v', '>']

cost = 1

def search():
    # ----------------------------------------
    # insert code here and make sure it returns the appropriate result
    # ----------------------------------------

    openList = [[0, init]]
    closed = []
    for i in range(len(grid)):
        closed.append([0]*len(grid[0]))
            
    while len(openList) > 0:
        (myCost, location) = openList.pop(0)
        closed[location[0]][location[1]] = 1
        
        for d in delta:
            # test valid
            next = [location[0]+d[0], location[1]+d[1]]
            if next[0]<0 or next[1]<0 or next[0]>=len(grid) or next[1]>=len(grid[0]):
                continue

            if closed[next[0]][next[1]]:
                continue

            if grid[next[0]][next[1]]:
                continue

            if next == goal:
                return [myCost+1] + next
            
            closed[next[0]][next[1]] = 1
            openList.append([myCost + 1, next])

    path = 'fail'
    return path # you should RETURN your result


print search()
