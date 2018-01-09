# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 13:21:34 2017

@author: Will Anthony

"""
from datetime import datetime
from datetime import time
from datetime import timedelta

import scipy as sp
import numpy as np

class TimeOfFlight:
    'Provides an abstracted method of calculating payload time to landing'


    def __init__(self):
        """
        Initialize a new payload.

        Inputs:
            Payload's current altitude
            Timestamp of that altitude reading

        Outputs:
            None

        Variables:
            altitude: Meters
            timestamp: datetime object
            landingalt: Altitude of projected landing site, MSL Meters
            time_to_land: datetime object, calculated using internal functions of the class object
            TTL_Valid: Valid/Invalid boolean flag to prevent false alarm
        """

        self.altitude = 0
        self.timestamp = datetime(2001, 9, 11, 9, 3, 0, 0) # Default value so comparisons don't throw type exception.
        self.landingalt = 0
        self.time_to_land = 0
        self.ttl_valid = False
        self.freefall_state = False
        self.freefall_count = 0



    def update(self, timestamp, altitude, landingalt = 0):

        """
        Performs a state update on the class object, prompting calculations and
        update of the output variable.

        Inputs:
            Timestamp of update (datetime object)
            Altitude of payload (meters)
            Altitude of predicted landing site (meters)

        Outputs:
            Datetime object (if update valid)
            Boolean False (if update invalid)

        """

        altitude_new = altitude
        timestamp_new = timestamp

        # FIXME detect first update and set base datetime object to be that, to avoid *huge* timedeltas from default

        #update the MSL altitude of predicted landing site if it changes
        if landingalt is not self.landingalt:
            self.landingalt = landingalt

        #check if the timestamps / altitudes are ordered.  If not, discard update
        if timestamp_new < self.timestamp:
            print('failed timestamp check')
            return False

        self.freefall_state = self._freefall_detection(altitude_new)

        if self.freefall_state is False:    # changed this to freefall state check
            print('Not in freefall')
            return False

        # should only execute if we are in freefall
        
        print('In freefall')
        delta_alt = abs(self.altitude - altitude_new)
        delta_t = abs(timestamp_new - self.timestamp)

        #set update values as object state variables
        self.altitude = altitude_new
        self.timestamp = timestamp_new

        fall_time = self._rawFalltime(delta_t, delta_alt, self.landingalt)
        #cubicFallTime = _rateOfDecentCubic()

        return fall_time

    def _freefall_detection(self, altitude):
        """
        Private (internal) function of the class object.

        Perfoms a very rudimentary freefall detection based on altitude deltas
        """

        if self.freefall_count >= 3:
            return True

        if altitude > self.altitude:
            self.altitude = altitude
            return False

        if self.altitude > altitude:
            self.freefall_count += 1




    def _rateOfDecentCubic(self):
        """
        Private (internal) function of the class object.

        Performs rate of decent calculation based on Cubic Spline Interpolation
        with simple extrapolation.

        This is expected to produce low levels of accuracy prior to entering "thick air".
        """
        falltime = None #safely initialize return variable

        #Calculate cubic spline function, with natural endpoints

        #Perform extrapolation to determine time at landing

        return falltime

    def _rawFalltime(self, delta_t, delta_alt, landing_alt):
        """
        Private (internal) function of the class object.

        Performs an unsophisticated "at this rate" time of fall calculation.
        """
        epsilon = 1e-3
        vel = delta_alt / delta_t.total_seconds()
        if vel < epsilon:
            print('velocity has gone to zero before altitude??')
            return 0
        if landing_alt < self.altitude:
            fall_dist = self.altitude - landing_alt
            falltime = fall_dist / vel
            return falltime
        
        print('payload below estimated landing altitude')
        return 0

    def _rateOfDecentExpo(self):
        """
        Private (internal) function of the class object.

        Performs rate of decent calculation based on exponential nature of
        atmospheric density.  The expression used has been determined from empirical
        data (curve fitting to payload decent data logs)
        """

        falltime = None

        return falltime

def Main():
    print('Class run standalone')

if __name__ == '__main__':
    Main()