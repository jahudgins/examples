# 
# Sailboat
# 
# Provides a sailboat to 
# Uses polar coordinates
#
 
from math import *
import random

class sailboat:

    # --------
    # init: 
    #   creates the sailboat
    #       location: (radius, bearing, heading)
    #       boom: degrees of boom (relative to boat heading)
    #       rudder: degrees of rudder (relative to boat heading)
    #
    def __init__(self, location, boom, rudder):
        self.location = location
        self.boom = boom
        self.rudder = rudder


    # update the sailboat
    def update(self):
        pass

    # location estimate:
    #   return estimatated location (lenth, degrees, orientation)
    
