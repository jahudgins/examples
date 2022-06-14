import math
import pdb

n = 4
maxValue = (1 << n)
ratio = 1.5
ratioMax = math.pow(ratio, (maxValue-1))
index = 0
last = 0
while index < (1 << n):
    next = pow(ratio, index) / ratioMax
    print index, next, next-last 
    last = next
    index += 1
