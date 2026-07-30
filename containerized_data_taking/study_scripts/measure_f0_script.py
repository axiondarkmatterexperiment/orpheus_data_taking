from motor_functions import coordinated_motion
from data_taking_functions import *
from fitting_functions import cavity_length_from_f0
import numpy as np

initial_span_GHz=0.04
initial_f0_GHz = 16.8784
tune_distance_cm=-0.5
tune_increment_cm = -0.005
measure_coupling=False
initial_cavity_length_cm = 13.809103

#Calculate actual cm increment from the number of steps taken:
steps_per_cm = 20000/0.127
tune_increment_steps = int(tune_increment_cm*steps_per_cm)


na_span_GHz = initial_span_GHz
na_fc_GHz = initial_f0_GHz
cavity_l_cm = initial_cavity_length_cm
num_steps = int(tune_distance_cm/tune_increment_cm)
estimated_f0_increment_GHz = tune_increment_cm*-1 #I roughly observe that contracting the cavity by 1cm increases frequency by 1 GHz
min_Q = 1000 #If measured Q is below this then ignore it and use this value
max_Q = 8000 #If measured Q is above this then ignore it and use this value
j=0
while j<num_steps:
    #Look at a wider window after tuning to find the f0 and rough estimate of QL. Don't log the measured cavity parameters
    #Why am I basing it on the Q and not the step size? 
    na_span_GHz=3*na_span_GHz
    na_fc, current_QL = log_transmission_scan(na_fc_GHz, na_span_GHz, param_logging=False)
    na_fc_hold = na_fc #This is to hold the first scanned fc value for this loop so that we can return to it if the mode is lost.
    time.sleep(0.1)
    na_fc_GHz = na_fc/1e9
    #Make the window smaller around the approximate peak and retake the transmission scan. Log the measured cavity parameters
    na_span_GHz = na_span_GHz/2
    na_fc, current_QL = log_transmission_scan(na_fc_GHz, na_span_GHz, param_logging=False)
    time.sleep(0.1)
    na_fc_GHz = na_fc/1e9
    if current_QL > min_Q and current_QL < max_Q:
        na_span_GHz = 5*na_fc_GHz/current_QL
    elif current_QL < min_Q:
        na_span_GHz = 5*na_fc_GHz/min_Q
    else:
        na_span_GHz = 5*na_fc_GHz/max_Q
    na_fc, current_QL = log_transmission_scan(na_fc_GHz, na_span_GHz, param_logging=True)
    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
    time.sleep(0.1)
    if measure_coupling and np.isnan(current_QL)==False:
        log_reflection_scan(na_fc_GHz, na_span_GHz/1.7, param_logging=True)
    #Only keep tuning if we have a good fit
    if np.isnan(current_QL)==False:
        print(str(timestamp) + "  --  measured QL = " + str(current_QL) + " -- measured f0 = " + str(np.trunc(na_fc/1e5)/1e4) + " GHz.")
        coordinated_motion(tune_increment_cm)
        cavity_l_cm = cavity_l_cm+tune_increment_steps/steps_per_cm
        cavity_l_cm_simulated = cavity_length_from_f0(na_fc/1e9)#Also log the cavity length from calculations based on simulations, to compare.
        log_cavity_params("cavity_length_cm", timestamp, cavity_l_cm)
        log_cavity_params("cavity_length_cm_simulated", timestamp, float(cavity_l_cm_simulated))
        time.sleep(0.1)
        j=j+1
    else:
        na_fc_GHz = na_fc_hold/1e9 #Presumably this is a good value to search at since the mode was lost in this loop and not before this loop and we have not tuned at all yet.
        na_span_GHz = initial_span_GHz #I think that reverting to the original window size is a good backup.
        print(str(timestamp) + " transmission scan failed or timed out, restarting loop at initial fc of scan and not tuning.")
