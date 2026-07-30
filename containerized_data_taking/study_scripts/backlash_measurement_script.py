from motor_functions import coordinated_motion
import time
from data_taking_functions import log_transmission_scan
import numpy as np

def measure_backlash(f0_initial_GHz, span_initial_GHz, steps_per):
    f0_current, Q_current = log_transmission_scan(f0_initial_GHz, span_initial_GHz)
    span_current = 5*f0_current/Q_current
    j=0
    while j<6:
        coordinated_motion(-0.005)
        f0_current, Q_current = log_transmission_scan(f0_current/1e9, span_current/1e9)
        span_current = 5*f0_current/Q_current
        j = j+1
    steps_per_cm = 20000/0.127
    one_step_in_cm = 1/steps_per_cm #One motor step

    f_array = [f0_current]
    steps_array = [0]
    j = 0
    while j<50:
        coordinated_motion(steps_per*one_step_in_cm)
        f0_current, Q_current = log_transmission_scan(f0_current/1e9, span_current/1e9)
        span_current = 5*f0_current/Q_current
        steps_current = (j+1)*steps_per
        f_array.append(f0_current)
        steps_array.append(steps_current)
        j=j+1
    return steps_array, f_array

steps_array, f_array = measure_backlash(16.198148,0.05,100)
np.savetxt("backlash_measurement_f0.txt",f_array)
np.savetxt("backlash_measurement_steps.txt",steps_array)
print(f_array)
print(steps_array)


#def measure_backlash(f0_initial_GHz, span_initial_GHz):
#    f0_array = []
#    steps_array = []
#    steps_per_cm = 20000/0.127
#    motion_size_cm = 0.01
#    motion_size_steps = int(motion_size_cm*steps_per_cm)
#    f0_current,Q_current = log_transmission_scan(f0_initial_GHz, span_initial_GHz)
#    steps_current = 0
#    f0_array.append(f0_current)
#    steps_array.append(steps_current)
#    f0_current_GHz = f0_current/1e9
#    span_current_GHz = 7*f0_current_GHz/Q_current
#
#    i=0
#    while i < 4:
#        j = 0
#        while j<5:
#            coordinated_motion(motion_size_cm)
#            steps_current = steps_current + motion_size_steps
#            time.sleep(1)
#            f0_current,Q_current = log_transmission_scan(f0_current_GHz,span_current_GHz)
#            f0_current_GHz = f0_current/1e9
#            span_current_GHz = 7*f0_current_GHz/Q_current
#            f0_array.append(f0_current)
#            steps_array.append(steps_current)
#            print(f0_current)
#            print(steps_current)
#            j = j+1
#
#        j = 0
#        while j<5:
#            coordinated_motion(-1*motion_size_cm)
#            steps_current = steps_current - motion_size_steps
#            time.sleep(1)
#            f0_current,Q_current = log_transmission_scan(f0_current_GHz,span_current_GHz)
#            f0_current_GHz = f0_current/1e9
#            span_current_GHz = 7*f0_current_GHz/Q_current
#            f0_array.append(f0_current)
#            steps_array.append(steps_current)
#            print(f0_current)
#            print(steps_current)
#            j = j+1
#
#        i = i+1
#    return steps_array, f0_array

#steps_arr, f0_arr = measure_backlash(16.337,0.05)
#print(steps_arr)
#print(f0_arr)
#f0_arr = np.asarray(f0_arr)
#steps_arr = np.asarray(steps_arr)
#np.savetxt("backlash_data_f0.txt",f0_arr)
#np.savetxt("backlash_data_steps.txt",steps_arr)
