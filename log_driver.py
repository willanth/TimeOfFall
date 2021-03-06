#!/usr/bin/env python

"""
Created on Thu Dec 28 19:15:34 2017

@author: Mark Jessop
@author: Will Anthony

"""

import datetime
import dateutil as du
import traceback
import tof
import sys

def read_telemetry_csv(filename,
    datetime_field = 0, 
    latitude_field = 3, 
    longitude_field = 4, 
    altitude_field = 5, 
    delimiter=','):
    '''
    Read in a Telemetry CSV file.
    Fields to use can be set as arguments to this function.
    By default we maintain compatability with the log files output by radiosonde_auto_rx, as they are good sources
    of flight telemetry data.
    These have output like the following:
    2017-12-27T23:21:59.560,M2913374,982,-34.95143,138.52471,719.9,-273.0,RS92,401.520
    <datetime>,<serial>,<frame_no>,<lat>,<lon>,<alt>,<temp>,<sonde_type>,<freq>

    Note that the datetime field must be parsable by dateutil.parsers.parse.

    If any fields are missing, or invalid, this function will return None.

    The output data is in the format:
    [
        [datetime (as a datetime object), latitude, longitude, altitude],
        [datetime (as a datetime object), latitude, longitude, altitude],
        ...
    ]
    '''

    output = []

    try:
        with open(filename, 'r') as file_in:
            for line in file_in:
                try:
                    # Split line by comma delimiters.
                    _fields = line.split(delimiter)
        
                    # Attempt to parse fields.
                    _datetime = du.parser.parse(_fields[datetime_field])
                    _latitude = float(_fields[latitude_field])
                    _longitude = float(_fields[longitude_field])
                    _altitude = float(_fields[altitude_field])
        
                    output.append([_datetime, _latitude, _longitude, _altitude])
                except:
                    traceback.print_exc()
                    return None
        
            file_in.close() #FIXME redunant since using the with?
        
            return output
        
    except IOError:
        print('Error opening ', filename)
        sys.exit()



def Main():
    # Basic test of the above function. Read in a file and print out the resultant array structure
    # import sys  # FIXME switched off for running in Spyder

    #variables used for testing making a tof object
    
    landingalt = 300

    filename = "20171226-232020_M2913209_RS92_401520.log"
    #filename = sys.argv[1]  # FIXME hardcoded this with a filename when running in Spyder

    #print(read_telemetry_csv(filename))
    track1 = tof.TimeOfFlight()

    print('\n\n')
    print('Using this data:')
    print('Choose from the following options:\n')
    print('1: Perform simple (velocity based) Time-to-Fall calculation\n')
    print('2: Perform cubic spline interpolation -> simple extrapolation\n')
    print('3: Perform atmospheric density based calculation\n')
    print('4: Perform multi-method Kalman filtered state prediction (wow!)\n')

    try:
        number = int(input('Choice: ')) #I'm sure there's a better way than casting?
    except:
        traceback.print_exc()
        
    # TODO File IO should be done using threading and async file IO

    if number is 1:
        print('This functionality is under construction\n')
        data = read_telemetry_csv(filename)
        for row in data:
            dt = row[0]
            alt = row[3]
            
            #print(str(dt) +' '+str(alt))
            falltime = track1.update(dt, alt, landingalt)
            print(falltime)
            
        print('Payload landed')


    if number is 2:
        print('This functionality is under construction\n')
    if number is 3:
        print('This functionality is under construction\n')
    if number is 4:
        print('This functionality is under construction\n')

    #call .join() to close threads out after file IO


if __name__ == '__main__':
    Main()
   