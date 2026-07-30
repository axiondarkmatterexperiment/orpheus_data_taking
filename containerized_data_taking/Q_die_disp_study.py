#The purpose of this is to check the simulations of the effects on Q of -3+3mm displacements of the top and bottom dielectric plates.
# The simulations simulated every combination of dielectric plate displacements in the -3 to +3 mm range with 0.2 mm resolution at 
# the simulations did this at cavity lengths ranging from 14.0-16.0cm with 0.1 cm resolution. I'd like to at least check a few of these points.

# This script will not change the length of the cavity. It is up to the operator to set the cavity length and the proper disk spacing.

from motor_functions import motor_command
from data_taking_functions import log_transmission_scan, log_reflection_scan, log_cavity_params
import numpy as np
from datetime import datetime as dt
##############################
## Variables we use:
##############################
BDP_IP = "192.168.25.3"
TDP_IP = "192.168.25.4"
CM_IP = "192.168.25.5"
port = 7776

steps_per_cm = 20000/0.127 #This is 157480.314961 steps per cm
backlash_steps = 1000 #This is measured empirically (room temp)
backlash_cm = backlash_steps/steps_per_cm
BDP_ratio = 4/5
TDP_ratio = 1/5

delta_increment = 0.02 #The units are cm
max_delta = 0.3

f_span_search = 0.1 #The units are GHz

cavity_length_cm = float(input('input the cavity length in cm'))
f3 = float(input('input the resonant frequency in Hz'))

increment_steps = steps_per_cm*delta_increment
max_delta_steps = steps_per_cm*max_delta
backlash_steps = 1000
##############################
##############################


##############################
### conduct the study:
##############################

#Move the bottom and top dielectric plates to -0.3cm displacement
motor_command(BDP_IP,"DI"+str(-max_delta_steps))
motor_command(TDP_IP,"DI"+str(-max_delta_steps))
#remove the backlash created by the above two lines.
motor_command(BDP_IP,"DI"+str(backlash_steps))
motor_command(TDP_IP,"DI"+str(backlash_steps))

deltas = np.arange(-max_delta, max_delta+increment_steps, increment_steps)

#Start the for loop for this cavity length:
for i in np.arange(2*max_delta/delta_increment+1):
    delta_bottom_cm = deltas[i] 
    for j in np.arange(2*max_delta/delta_increment+1):
        timestamp = dt.now(pytz.timezone('US/Pacific')).timestamp()
        data_id = int(timestamp*1000)

        delta_top_cm = deltas[j]
        #Transmission scan to find the peak:
        f0,Q0 = log_transmission_scan(f3/1e9,f_span_search, fitting=True, param_logging=False)
        
        f_span = (f0/Q0)/1e9
        #Three transmission scans to measure Q:
        f1,Q1 = log_transmission_scan(f0/1e9,f_span, fitting=True, param_logging=True, data_id=data_id)
        f_span = (f1/Q1)/1e9
        f2,Q2 = log_transmission_scan(f1/1e9,f_span, fitting=True, param_logging=True, data_id=data_id)
        f_span = (f2/Q2)/1e9
        f3,Q3 = log_transmission_scan(f2/1e9,f_span, fitting=True, param_logging=True, data_id=data_id)
        
        log_cavity_params('Q_avg_die_disp_study', timestamp, np.mean(np.asarray([Q1,Q2,Q3])), data_id=data_id)
        log_cavity_params('f_avg_die_disp_study', timestamp, np.mean(np.asarray([f1,f2,f3])), data_id=data_id)
        log_cavity_params('Q_std_die_disp_study', timestamp, np.std(np.asarray([Q1,Q2,Q3])), data_id=data_id)
        log_cavity_params('f_std_die_disp_study', timestamp, np.std(np.asarray([f1,f2,f3])), data_id=data_id)
        log_cavity_params('cavity_length_cm', timestamp, cavity_length_cm, data_id=data_id)
        log_cavity_params('delta_bottom_cm', timestamp, delta_bottom_cm, data_id=data_id)
        log_cavity_params('delta_top_cm', timestamp, delta_top_cm, data_id=data_id)

        motor_command(TDP_IP,"DI"+str(increment_steps))

    #Remove backlash in the TDP:
    motor_command(TDP_IP,"DI"+str(-backlash_steps))
    #Return TDP to the starting position of delta=-3mm:
    motor_command(TDP_IP, "DI"+str(-max_delta_steps))
    #move forward through the BDP delta values array:
    motor_command(BDP_IP,"DI"+str(increment_steps))

#Move us back to the starting point, where deltas are both zero
motor_command(TDP_IP,"DI"+str(-max_delta_steps/2))
motor_command(BDP_IP,"DI"+str(-max_delta_steps/2))
