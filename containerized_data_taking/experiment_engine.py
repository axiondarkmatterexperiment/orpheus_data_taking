from state import state
from data_taking_functions import *
from motor_functions import coordinated_motion
import time
import sys
steps_per_cm = 20000/0.127

def take_data():

    loop_counter = 1
    state.run_status=True
    while True:
        with state.lock:
            pause = state.pause
        if pause:
            state.last_task = "Experiment runner is paused"

        #Prototypical data taking action structure:
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
                na_fc, transmission_Q = log_transmission_scan(na_fc, na_span)
                timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
                last_task = "Transmission:"+str(timestamp)
                with state.lock:
                    state.na_fc = float(na_fc/1e9)
                    #na_fc is changed by the data taker sometimes in order to guide the NA. This value is only ever set by the transmission scan, and is used for setting the fc of the digitization
                    state.transmission_f0 = float(na_fc/1e9) 
                    state.transmission_Q = float(transmission_Q)
                    state.na_span = float(na_span)
                    state.last_task = last_task
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log_error(timestamp, repr(e) + "--line No." + str(exc_tb.tb_lineno))
                state.error_msg = repr(e) + "--line No. " + str(exc_tb.tb_lineno)
            
        #reflection scan:
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
                na_fc, reflection_Q, beta = log_reflection_scan(na_fc, na_span)
                timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
                last_task = "Reflection:"+str(timestamp)
                with state.lock:
                    state.na_fc = float(na_fc/1e9)
                    state.beta = float(beta)
                    state.last_task = last_task
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
                start_timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
                last_task = "Digitization fc="+str(lo_freq)+" Start:"+str(start_timestamp)
                start_digitization(30)
                with state.lock:
                    state.last_task = last_task
                finish_timestamp, freqs, pows, = wait_for_digitization(return_digitization=True)
                log_digitization(start_timestamp, freqs, pows) #I would rather log the start timestamp instead of the finish timestamp
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
                    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
                    last_task = "Tuning start:"+str(timestamp)
                    #move the motors:
                    coordinated_motion(dl_cm)
                    true_dl_cm = int(steps_per_cm*dl_cm)/steps_per_cm #Account for the fact that steps are integers and can't achieve exact precision in centimeters
                    #Update the GUI message tile:
                    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
                    last_task = "Tuning finished:"+str(timestamp)
                    #Update cavity length variable
                    cavity_length = cavity_length + true_dl_cm
                    #Update state object:
                    with state.lock:
                        state.cavity_length = float(cavity_length)
                        state.last_task = last_task
                    #Update the hard-written file that keeps track of the current length of the cavity
                    with open('cavity_current_length.txt', 'w') as f:
                        f.write(str(cavity_length))
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log_error(timestamp, repr(e) + "--line No." + str(exc_tb.tb_lineno))
                state.error_msg = repr(e) + "--line No. " + str(exc_tb.tb_lineno)


        loop_counter = loop_counter + 1
    state.run_status=False
