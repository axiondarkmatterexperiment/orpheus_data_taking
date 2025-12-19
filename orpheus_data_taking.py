##########################################################################################################
###                                                                                                    ###
### This script runs the Orpheus data taking and sets up an interactive and self-updating GUI          ###
### that reports the status of the experiment to a remote or local operator. You do not need           ###
### to SSH into the orpheus computer to run it, but you need to be connected to the CENPA network      ###
### either through ethernet or VPN.  -Jimmy                                                            ###
###                                                                                                    ###
##########################################################################################################


from blessed import Terminal
from OrpheusGUI import OrpheusGUI
from OrpheusOperator import OrpheusOperator
from monitoring_functions import *
from motor_functions import coordinated_motion
from data_taking_functions import log_transmission_scan, log_reflection_scan
import datetime
import pytz
import time
import sys
import os
import numpy as np
import TextUI
import threading

current_cavity_l = float(np.genfromtxt('cavity_current_length.txt',delimiter=','))
cavity_l_array = np.genfromtxt('cavity_lengths_array.csv',delimiter=',')


term = Terminal()
GUI=OrpheusGUI()
Operator=OrpheusOperator()

#This is to run the full data taking cadence, which is separate from logging the sensor values
def take_data(name):
    #Count the loops to have differing periods for different actions
    tuning_index = 0 #for indexing through the list of cavity lengths, back and forth
    loop_counter = 1
    tune_forward = True
    Operator.cavity_length = current_cavity_l
    
    while True:
        #Transmission Scan:
        timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
        if Operator.transmission_period != 0:
            if loop_counter % Operator.transmission_period == 0:
                try:
                    GUI.na_fc_tile.set_value(float(Operator.na_fc))
                    GUI.na_span_tile.set_value(float(Operator.na_span))
                    GUI.update_ui(term)
                    f0,Q = log_transmission_scan(np.float64(Operator.na_fc), np.float64(Operator.na_span))
                    GUI.Q_tile.set_value(Q)
                    GUI.f0_tile.set_value(f0/1e9)
                    #Q_width = f0/Q
                    #Operator.na_span = str(Q_width*Operator.na_Q_widths)
                    Operator.na_fc = str(f0/1e9)
                    GUI.message_tile.text="Transmission:"+str(timestamp)
                    GUI.update_ui(term)
                except (TypeError, ZeroDivisionError):
                    GUI.message_tile.text="Transmission fail" + str(timestamp)
        
        #Reflection Scan:
        timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
        if Operator.reflection_period != 0:
            if loop_counter % Operator.reflection_period == 0:
                try:
                    f0_refl,Q_refl,beta = log_reflection_scan(np.float64(Operator.na_fc), np.float64(Operator.na_span))
                    GUI.beta_tile.set_value(beta)
                    GUI.message_tile.text="Reflection:"+str(timestamp)
                    GUI.update_ui(term)
                except (TypeError, ZeroDivisionError):
                    GUI.message_tile.text="Reflection fail:"+str(timestamp)
                    GUI.update_ui(term)

        #Cavity Tuning:
        if Operator.tuning_period != 0:
            if loop_counter % Operator.tuning_period == 0:
                try:
                    GUI.message_tile.text="starting tuning operation " + str(Operator.dl_cm)
                    l_cm = Operator.cavity_length
                    dl_cm = l_cm - cavity_lengths_array[tuning_index]
                    time.sleep(1)
                    GUI.update_ui(term)
                    coordinated_motion(Operator.dl_cm)
                    Operator.cavity_length = Operator.cavity_length + dl_cm
                    GUI.cavity_length_tile.set_value(Operator.cavity_length)
                    GUI.message_tile.text="done with tuning operation"
                    GUI.update_ui(term)
                    with open('cavity_current_length.txt','w') as output:
                        output.write(str(Operator.cavity_length))
                    #Determine the direction of tuning. The data taking is set up to scan and re-scan back and forth through the array of cavity lengths.
                    if tune_forward:
                        tuning_index = tuning_index + 1
                    else:
                        tuning_index = tuning_index - 1
                    if tuning_index == 0:
                        tune_forward = True
                        GUI.tuning_mode_tile.text="Tuning Forward"
                    if tuning_index == len(cavity_lengths_array)-1:
                        tune_forward = False
                        GUI.tuning_mode_tile.text="Tuning Backward"
                    time.sleep(3)
                except:
                    GUI.message_tile.text= "error during tuning"
                    GUI.update_ui(term)
                    time.sleep(3)

        #Digitize Gray will inform me about this later
        #digitize(f0,dig_span,

        #Widescan every 20 cycles:
        #if loop_counter%20==0:
            #log_transmission_scan(np.float64(Operator.widescan_fc), np.float64(Operator.widescan_span), np.float64(Operator.widescan_power), np.float64(Operator.widescan_N_avgs))
        
        loop_counter = loop_counter+1
        

def sensor_monitoring(name):
    while True:
        log_sensors()#different from log_sensor()

def run_GUI():
    establish_databases()
    internal_thread = threading.Thread(target=take_data, args=("data_taker",))
    internal_thread.start()
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        GUI.initialize_ui()
        GUI.update_ui(term)
        while True:
            val=term.inkey(timeout=0.1)
            if val:
                if val.name=="KEY_ENTER":
                    input_str=GUI.input_tile.text
                    GUI.input_tile.text=""
                    if input_str=="quit":
                        internal_thread.stop()
                        quit()
                    else:
                        entity_str = input_str[0:input_str.find(',')]
                        val_str = input_str[(input_str.find(',')+1):]
                        #Catalogue of entities:
                        catalogue = np.asarray(["na_power", "na_fc", "na_span", "dl_cm", "transmission_period", "reflection_period", "tuning_period"])
                        cat_idx = np.argwhere(catalogue==entity_str)
                        #If an item in the catalogue has been selected, update the DAQ variable, which is always a string
                        if np.size(cat_idx)>0:
                            exec("Operator."+entity_str+"="+val_str)
                            #exec("GUI."+entity_str+"_tile.set_value("+val_str+")")
                            exec("GUI."+entity_str+"_tile.set_value(Operator."+entity_str+")")
                else:
                    GUI.input_tile.handle_key(val)
                GUI.update_ui(term)
    term.exit_fullscreen()

run_GUI()

#establish_databases()
#thread1 = threading.Thread(target=run_GUI, args=("GUI_runner",))
#thread2 = threading.Thread(target=take_data, args=("data_taker",))
#thread3 = threading.Thread(target=take_data, args=("sensor_monitor",))

#thread1.start()
#thread2.start()
#thread3.start()
