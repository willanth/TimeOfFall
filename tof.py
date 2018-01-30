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
        self.burst_time = None



    def update(self, upd_sent, landingalt = 0, method = 1):

        """
        Performs a state update on the class object, prompting calculations and
        update of the output variable.

        Inputs:
            List of telemetry information from the payload in Jessop Format
            Altitude of predicted landing site (meters)
            Time of Flight calculation method

        Outputs:
            Datetime object (if update valid)
            Boolean False (if update invalid)

        """
        # bail on an invalid or corrupted telem sentance 
        if self._validateTelemetry is False:
            return False
        
        #check if the timestamps / altitudes are ordered.  If not, discard update
        if upd_sent[0] < self.timestamp:
            print('failed timestamp check')
            return False
        
        self.telem_list.append(upd_sent)
        # if there is only one entry in the list (new object) set timestamp
        if len(self.telem_list) == 1:
            self.timestamp = self.telem_list[0][0]

        #update the MSL altitude of predicted landing site if it changes
        if landingalt is not self.landingalt:
            self.landingalt = landingalt

        if self.freefall_state is False:    # changed this to freefall state check
            print('Not in freefall')
            self.ttl_valid = False
            self.freefall_state = self._freefall_detection(upd_sent)
            return False

        # should only execute if we are in freefall
        print('In freefall')
        # only log frames after burst detection fires, we don't care about before that
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
            self.ttl_valid = True

        return fall_time

    def _freefall_detection(self, telem_frame):
        """
        Private (internal) function of the class object.

        Perfoms a very rudimentary freefall detection based on altitude deltas
        
        """
        if isinstance(telem_frame[3], float) is False:    #A cave-dwelling typecheck
            return False
        
        if self.freefall_state is True: #in case we are accidentally called having already triggered
            return True
        
        if self.freefall_count < -4:
            self.burst_time = telem_frame[0]
            return True

        if telem_frame[3] > self.altitude:
            self.altitude = telem_frame[3]
            if self.freefall_count < 10:
                self.freefall_count += 1
            
            return False

        if self.altitude > telem_frame[3]:
            self.freefall_count -= 1
            return False


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

        for row in self.telem_list:
            #FIXME crashes as the datetime value may be Null/None as telem_list isn't being appended correctly
            delta_seconds.append(timedelta.total_seconds(abs(self.burst_time - row[0])))
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
    
    def _validateTelemetry(self, update_sentance):
        """
        Private (internal) function of the class object.

        Checks the telemetry sentance for corruption or missing entries.

        Inputs:
            Telemetry sentance in Jessop Format
            
        Outputs:
            Boolean
        """
        
        # cursory length check
        if len(update_sentance) < 9:
            return False

        # altitude should be positive at all times
        if update_sentance[5] < 0:
            return False
        
        # datetime should not be null / corrupted
        if isinstance(update_sentance[0], datetime):
            pass
        
        
def Main():
    print('Class run standalone')

if __name__ == '__main__':
    Main()
