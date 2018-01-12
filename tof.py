# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 13:21:34 2017

@author: Will Anthony

"""
from datetime import datetime
#from datetime import time
from datetime import timedelta

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
import matplotlib.pyplot as plt

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
        self.telem_list = []



    def update(self, upd_sent, landingalt = 0, method = 1):

        """
        Performs a state update on the class object, prompting calculations and
        update of the output variable.

        Inputs:
            List of telemetry information from the payload in Jessop Format
            Altitude of predicted landing site (meters)

        Outputs:
            Datetime object (if update valid)
            Boolean False (if update invalid)

        """
        
        # TODO as new update sentances are passed in, append them to the update
        # list so that the algorithms have access to historical data
        
        
        # if there is only one entry in the list (new object) set timestamp
        if len(self.telem_list) == 1:
            self.timestamp = self.telem_list[0][0]


        #update the MSL altitude of predicted landing site if it changes
        if landingalt is not self.landingalt:
            self.landingalt = landingalt

        #check if the timestamps / altitudes are ordered.  If not, discard update
        if upd_sent[0] < self.timestamp:
            print('failed timestamp check')
            return False

        self.freefall_state = self._freefall_detection(upd_sent[3])

        if self.freefall_state is False:    # changed this to freefall state check
            print('Not in freefall')
            self.ttl_valid = False
            return False

        # should only execute if we are in freefall
        print('In freefall')
        # only log frames after burst detection fires, we don't care about before that
        self.telem_list.append(upd_sent)
        delta_alt = abs(self.altitude - upd_sent[3])
        delta_t = abs(upd_sent[0] - self.timestamp)

        #set update values as object state variables
        self.altitude = upd_sent[3]
        self.timestamp = upd_sent[0]

        if method == 1:
            
            fall_time = self._rawFalltime(delta_t, delta_alt, self.landingalt)
            self.ttl_valid = True
            
        elif method == 2:
            
            fall_time = self._rateOfDecentCubic()

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

        #initialize new lists because I'm not sure what I want to do with this yet
        delta_seconds = []
        alt = []
        
        # FIXME this is getting time and altitude information PRE BURST which is not helpful
        for row in self.telem_list:
            delta_seconds.append(timedelta.total_seconds(abs(self.telem_list[0][0] - row[0])))
            alt.append(row[3])
            
        xi = np.array(delta_seconds)
        yi = np.array(alt)
        # positions to inter/extrapolate
        x = np.linspace(0, len(delta_seconds), len(delta_seconds))
        # spline order: 1 linear, 2 quadratic, 3 cubic ... 
        order = 3
        # do inter/extrapolation
        s = InterpolatedUnivariateSpline(xi, yi, k=order)
        y = s(x)

        # Now find the value at which the function reaches the estimated landing altitude
        # Suggest Bisection ( O(log n) ) or Secant variant of Newton-Raphson 
        
        # TODO solving for x given y?  Easy solution is what happens at f(x)=0 as that root will be time t

        # plot is only for debug!
        plt.figure()
        plt.plot(xi, yi)
        s = InterpolatedUnivariateSpline(xi, yi, k=order)
        y = s(x)
        plt.plot(x, y)
        plt.show()
        
        return falltime

    def _rawFalltime(self, delta_t, delta_alt, landing_alt):
        """
        Private (internal) function of the class object.

        Performs an unsophisticated "at this rate" time of fall calculation.
        """

        # TODO: Exception Handling, and evaluate the output this vs the known time from the logfile
        # TODO: Some kind of weighted averaging?  Lots of jitter sample-to-sample
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

        pass
    
    def _rateOfDecentKalman(self):
        """
        Private (internal) function of the class object.
        
        Uses a recursive state prediction algorithm (notionally Kalman) to 
        project a state vector.  As we get quite a few samples it should 
        converge well?
        """
        
        pass

def Main():
    print('Class run standalone')

if __name__ == '__main__':
    Main()
