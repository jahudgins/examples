# 
# Sailboat Environment
# 
# Provides a world environment to simulate sailing.
# Uses polar coordinates
#
 
from math import *
import random

class environment:

    # --------
    # init: 
    #   creates the environment
    #       wind_prevailing: prevailing wind (velocity, degrees)
    #       wind_distribution: distribution (std. dev.) of wind (velocity, degrees)
    #       wind_variability: proportion to change the wind each frame
    #       measurement_error: proportion of measurement error (distance, degrees)
    #
    def __init__(self, wind_prevailing, wind_distribution, wind_variability):
        self.wind_prevailing = wind_prevailing
        self.wind_distribution = wind_distribution
        self.wind_variability = wind_variability

        # todo: calculate initial wind
        self.current_wind = self.wind_prevailing


    # wind:
    #   return current wind velocity and direction
    def wind(self):
        return self.current_wind

    # update:
    #   update the environment
    def update(self):
        pass
        # todo: update wind (1-a)*current + a*new_random (based on prevailing and distribution)

    # measure_landmark:
    #   return the location of the landmark (radius, degrees) and measured distance, degrees
    #       sailboat: the sailboat to make measurements
    #       landmark_index: the index of landmark to measure
    def measure_landmark(self, sailboat, landmark_index):
        # todo: calculate actual distance, degrees
        # todo: adjust actual by measurement error
        return ((1.0, 0.0), (1.0, 0.0))
    
