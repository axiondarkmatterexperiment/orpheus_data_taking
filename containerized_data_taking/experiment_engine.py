from state import state
from data_taking_functions import *
from fitting_functions import f0_from_cavity_length
from motor_functions import coordinated_motion
from monitoring_functions import *
import time
import sys
from datetime import datetime as dt
steps_per_cm = 20000/0.127

def take_data():

    loop_counter = 1
    state.run_status=True
    while True:
        with state.lock:
            pause = state.pause
            #state.update_json()
        if pause:
            state.last_task = "Experiment runner is paused"

        data_taking_id = int(dt.now(pytz.timezone('US/Pacific')).timestamp()*1000)
        
        ##Scan all sensors:
        ##1- check the latest updated value of the period of the action and check if data taker has requested shut-down:
        #with state.lock:
        #    run_condition = state.run_condition
        #    pause = state.pause
        #    
        ##2- take action if requirements are met
        #if pause == False:
        #    try:
        #        timestamp = dt.now(pytz.timezone('US/Pacific'))
        #        log_sensors()
        #        last_task = "sensors:"+str(timestamp)
        #    except Exception as e:
        #        exc_type, exc_obj, exc_tb = sys.exc_info()
        #        log_error(timestamp, repr(e) + "--line No." + str(exc_tb.tb_lineno))
        #        state.error_msg = repr(e) + "--line No. " + str(exc_tb.tb_lineno)


        #Transmission scan:
        #1- check the latest updated value of the period of the action and check if data taker has requested shut-down:
        with state.lock:
            transmission_period = state.transmission_period
            run_condition = state.run_condition
            pause = state.pause
            
            #Relevant experiment parameters
            na_fc = state.na_fc
            transmission_Q = state.transmission_Q
            na_transmission_Q_widths = state.na_transmission_Q_widths
            
        #2- take action if requirements are met
        if transmission_period != 0 and loop_counter % transmission_period == 0 and pause == False:
            try:
                Q_width = na_fc/transmission_Q
                na_span = Q_width*na_transmission_Q_widths
                #wider window without param logging just to search for the peak
                na_fc, trash_Q = log_transmission_scan(na_fc,1.5*na_span,n_avgs = 1, fitting=True,param_logging=False)
                na_fc = na_fc/1e9
                #regular window with param logging to measure Q
                na_fc, transmission_Q = log_transmission_scan(na_fc, na_span, data_id=data_taking_id)
                timestamp = dt.now(pytz.timezone('US/Pacific'))
                last_task = "Transmission:"+str(timestamp)
                with state.lock:
                    state.na_fc = float(na_fc/1e9)
                    #na_fc is changed by the data taker sometimes in order to guide the NA. This value is only ever set by the transmission scan, and is used for setting the fc of the digitization
                    state.transmission_f0 = float(na_fc/1e9) 
                    state.transmission_Q = float(transmission_Q)
                    state.na_span = float(na_span)
                    state.last_task = last_task
                    state.update_json()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                timestamp = dt.now(pytz.timezone('US/Pacific'))
                log_error(timestamp, repr(e) + "--line No." + str(exc_tb.tb_lineno))
                state.error_msg = repr(e) + "--line No. " + str(exc_tb.tb_lineno)
            
        #Reflection scan:
        #1- check the latest updated value of the period of the action and check if data taker has requested shut-down:
        with state.lock:
            reflection_period = state.reflection_period
            run_condition = state.run_condition
            pause = state.pause
            
            #Relevant experiment parameters
            na_fc = state.na_fc
            transmission_Q = state.transmission_Q #I use transmission Q to determine the reflection scan window size because reflection fits are less reliable
            na_reflection_Q_widths = state.na_reflection_Q_widths
            
        #2- take action if requirements are met
        if reflection_period != 0 and loop_counter % reflection_period == 0 and pause == False:
            try:
                Q_width = na_fc/transmission_Q
                na_span = Q_width*na_reflection_Q_widths
                na_fc, reflection_Q, beta = log_reflection_scan(na_fc, na_span, data_id=data_taking_id)
                timestamp = dt.now(pytz.timezone('US/Pacific'))
                last_task = "Reflection:"+str(timestamp)
                with state.lock:
                    state.na_fc = float(na_fc/1e9)
                    state.beta = float(beta)
                    state.last_task = last_task
                    state.update_json()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log_error(timestamp, repr(e) + "--line No." + str(exc_tb.tb_lineno))
                state.error_msg = repr(e) + "--line No. " + str(exc_tb.tb_lineno)
            
        #Widescan:
        #1- check the latest updated value of the period of the action and check if data taker has requested shut-down:
        with state.lock:
            widescan_period = state.widescan_period
            run_condition = state.run_condition
            pause = state.pause
            
        #2- take action if requirements are met
        if widescan_period != 0 and loop_counter % widescan_period == 0 and pause == False:
            try:
                log_transmission_widescan(15.5,17.3, data_id=data_taking_id)
                timestamp = dt.now(pytz.timezone('US/Pacific'))
                last_task = "Widescan:"+str(timestamp)
                with state.lock:
                    state.last_task = last_task
                    state.update_json()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log_error(timestamp, repr(e) + "--line No." + str(exc_tb.tb_lineno))
                state.error_msg = repr(e) + "--line No. " + str(exc_tb.tb_lineno)
            
        #Digitizing:
        #1- check the latest updated value of the period of the action and check if data taker has requested shut-down:
        with state.lock:
            digitization_period = state.digitization_period
            run_condition = state.run_condition
            pause = state.pause
            
            #Relevant experiment parameters
            transmission_f0 = state.transmission_f0
            
        #2- take action if requirements are met
        if digitization_period != 0 and loop_counter % digitization_period == 0 and pause == False:
            try:
                lo_set_freq = int(float(transmission_f0)*1e9*100)/100 #Set the frequency to a resolution of a hundredth of a Hz. Higher precision is rejected by the LO.
                lo_freq = set_lo_center_freq(lo_set_freq)
                start_timestamp = dt.now(pytz.timezone('US/Pacific'))
                last_task = "Digitization fc="+str(lo_freq)+" Start:"+str(start_timestamp)
                start_digitization(30)
                with state.lock:
                    state.last_task = last_task
                finish_timestamp, freqs, pows, = wait_for_digitization(return_digitization=True)
                log_digitization(start_timestamp, freqs, pows, data_id = data_taking_id) #I would rather log the start timestamp instead of the finish timestamp
                last_task = "Digitization fc="+str(lo_freq)+" End:"+str(finish_timestamp)
                with state.lock:
                    state.last_task = last_task
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log_error(timestamp, repr(e) + "--line No." + str(exc_tb.tb_lineno))
                state.error_msg = repr(e) + "--line No. " + str(exc_tb.tb_lineno)

            
        #Tuning:
        #1- check the latest updated value of the period of the action and check if data taker has requested shut-down:
        with state.lock:
            tuning_period = state.tuning_period
            run_condition = state.run_condition
            pause = state.pause
            
            #Relevant experiment parameters
            cavity_length = state.cavity_length
            max_cavity_length = state.max_cavity_length
            min_cavity_length = state.min_cavity_length
            dl_cm = state.dl_cm

        #2- take action if requirements are met
        if tuning_period != 0 and loop_counter % tuning_period == 0 and pause == False:
            try:
                if cavity_length <= max_cavity_length and cavity_length >= min_cavity_length:
                    #Update the GUI message tile:
                    timestamp = dt.now(pytz.timezone('US/Pacific'))
                    last_task = "Tuning start:"+str(timestamp)
                    #move the motors:
                    coordinated_motion(dl_cm)
                    true_dl_cm = int(steps_per_cm*dl_cm)/steps_per_cm #Account for the fact that steps are integers and can't achieve exact precision in centimeters
                    #Update the GUI message tile:
                    timestamp = dt.now(pytz.timezone('US/Pacific'))
                    last_task = "Tuning finished:"+str(timestamp)
                    #Update cavity length variable
                    cavity_length = cavity_length + true_dl_cm
                    log_cavity_params('cavity_length_cm', timestamp, cavity_length, data_id = data_taking_id)
                    #Update state object:
                    with state.lock:
                        state.cavity_length = float(cavity_length)
                        state.last_task = last_task
                        state.update_json()
                    #Update the hard-written file that keeps track of the current length of the cavity
                    #with open('data/cavity_current_length.txt', 'w') as f:
                    #    f.write(str(cavity_length))

                #conditions for turning around the cavity tuning motion
                elif cavity_length > max_cavity_length and dl_cm > 0:
                    #First get past the backlash, which is about 1000 steps (measured in ELog 1166)
                    coordinated_motion(-1000/steps_per_cm) #Backlash is about 1000 steps
                    #now re-enter the tuning range:
                    coordinated_motion(max_cavity_length - cavity_length - 0.01) #Return to the upper limit of the tuning range, with an extra nudge to ensure we don't get stuck outside of it.
                    cavity_length = max_cavity_length - 0.01
                    log_cavity_params('cavity_length_cm', timestamp, cavity_length, data_id = data_taking_id)
                    estimated_f0 = f0_from_cavity_length(max_cavity_length - 0.01) #This function returns the estimated f0 in GHz. It is based on room temp measurements, though. It has about 10 MHz accuracy.
                    timestamp = dt.now(pytz.timezone('US/Pacific'))
                    last_task = "turning around:"+str(timestamp)
                    with state.lock:
                        state.cavity_length = float(cavity_length)
                        state.dl_cm = -dl_cm #Turns the cavity tuning around
                        state.na_fc = estimated_f0
                        state.last_task = last_task
                        state.update_json()
                elif cavity_length < min_cavity_length and dl_cm < 0:
                    #First get past the backlash, which is about 1000 steps (measured in ELog 1166)
                    coordinated_motion(1000/steps_per_cm) #Backlash is about 1000 steps
                    #now re-enter the tuning range:
                    coordinated_motion(min_cavity_length - cavity_length + 0.01) #Return to the lower limit of the tuning range, with an extra nudge to ensure we don't get stuck outside of it.
                    cavity_length = min_cavity_length + 0.01
                    log_cavity_params('cavity_length_cm', timestamp, cavity_length, data_id = data_taking_id)
                    estimated_f0 = f0_from_cavity_length(min_cavity_length + 0.01) #This function returns the estimated f0 in GHz. It is based on room temp measurements, though. It has about 10 MHz accuracy.
                    timestamp = dt.now(pytz.timezone('US/Pacific'))
                    last_task = "turning around:"+str(timestamp)
                    with state.lock:
                        state.cavity_length = float(cavity_length)
                        state.dl_cm = -dl_cm #Turns the cavity tuning around
                        state.na_fc = estimated_f0
                        state.last_task = last_task
                        state.update_json()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log_error(timestamp, repr(e) + "--line No." + str(exc_tb.tb_lineno))
                state.error_msg = repr(e) + "--line No. " + str(exc_tb.tb_lineno)

        with state.lock:
            pause = state.pause
        if pause == False:
            loop_counter = loop_counter + 1
    state.run_status=False
