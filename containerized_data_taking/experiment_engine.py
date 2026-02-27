from state import state
from data_taking_functions import *
import time

def take_data():

    loop_counter = 1
    state.run_status=True
    while True:

        with state.lock:
            run_condition = state.run_condition
            transmission_period = state.transmission_period
            na_fc = float(state.na_fc)
            na_span = float(state.na_span)

        if not run_condition:
            break

        if transmission_period != 0 and loop_counter % transmission_period == 0:
            fc_meas, Q_meas = log_transmission_scan(na_fc/1e9, na_span/1e9)
            print("f0 = "+str(fc_meas))
            print("Q = " + str(Q_meas))

        loop_counter = loop_counter + 1
    state.run_status=False
