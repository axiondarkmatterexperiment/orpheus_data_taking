from state import state
from data_taking_functions import *
import time
import sys

def take_data():

    loop_counter = 1
    state.run_status=True
    while True:
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
                    state.transmission_Q = float(transmission_Q)
                    state.last_task = last_task
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                log_error(timestamp, repr(e) + "--line No." + str(exc_tb.tb_lineno))
                state.error_msg = repr(e) + "--line No. " + str(exc_tb.tb_lineno)
            

        loop_counter = loop_counter + 1
    state.run_status=False
