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
from data_taking_functions import log_transmission_scan, log_reflection_scan, start_digitization, set_lo_center_freq, wait_for_digitization, log_cavity_params, log_digitization
import datetime
import pytz
import time
import sys
import os
import numpy as np
import TextUI
import threading

current_cavity_l = float(np.genfromtxt('cavity_current_length.txt',delimiter=','))
cavity_lengths_array = np.genfromtxt('cavity_lengths_array.txt',delimiter=',')
steps_per_cm=20000/0.127

term = Terminal()
GUI=OrpheusGUI()
Operator=OrpheusOperator()

#This is to run the full data taking cadence, which is separate from logging the sensor values
def take_data(name):
    #Count the loops to have differing periods for different actions
    tuning_index = 0 #for indexing through the list of cavity lengths, back and forth
    loop_counter = 1
    tune_forward = True #This variable will not be necessary if I do not use the array of desired cavity lengths
    Operator.cavity_length = current_cavity_l
    GUI.cavity_length_tile.set_value(current_cavity_l)
    GUI.max_cavity_length_tile.set_value(Operator.max_cavity_length)
    GUI.min_cavity_length_tile.set_value(Operator.min_cavity_length)
    GUI.na_transmission_Q_widths_tile.set_value(Operator.na_transmission_Q_widths)
    GUI.na_reflection_Q_widths_tile.set_value(Operator.na_reflection_Q_widths)
    
    while Operator.run_condition:
        #Poll Sensors:
#        timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
#        if Operator.sensors_period != 0 and Operator.run_condition:
#            if loop_counter % Operator.sensors_period == 0:
#                try:
#                    log_hall_sensors()
#                    log_magnet_temps()
#                    log_insert_temps()
#

        #Don't do anything if paused:
        if Operator.pause:
            GUI.message_tile.text="Data taking paused. Enter command 'resume' to unpause."
            GUI.update_ui(term)
            while Operator.pause:
                time.sleep(0.5)


        #Transmission Scan:
        timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
        if Operator.transmission_period != 0 and Operator.run_condition:
            if loop_counter % Operator.transmission_period == 0:
                try:
                    Q_width = float(Operator.na_fc)/Operator.transmission_Q
                    GUI.na_fc_tile.set_value(float(Operator.na_fc))
                    Operator.na_transmission_span = str(Q_width*Operator.na_transmission_Q_widths)
                    GUI.na_span_tile.set_value(float(Operator.na_transmission_span))
                    GUI.update_ui(term)
                    f0,Q = log_transmission_scan(np.float64(Operator.na_fc), np.float64(Operator.na_transmission_span))
                    GUI.Q_tile.set_value(Q)
                    GUI.f0_tile.set_value(f0/1e9)
                    Operator.transmission_Q = Q
                    Q_width = f0/Q
                    Operator.na_transmission_span = str(Q_width*Operator.na_transmission_Q_widths)
                    Operator.na_fc = str(f0/1e9)
                    GUI.message_tile.text="Transmission:"+str(timestamp)
                    GUI.update_ui(term)
                #except (TypeError, ZeroDivisionError):
                #    GUI.message_tile.text="Transmission fail: " + str(timestamp)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    log_error(timestamp,repr(e))
                    GUI.message_tile.text="Transmission fail:"+str(timestamp)
                    #GUI.error_tile.text=repr(e)
                    GUI.error_tile.text=(repr(e) + "-- line No. " + str(exc_tb.tb_lineno))
                    GUI.update_ui(term)
        
        #Reflection Scan:
        timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
        if Operator.reflection_period != 0 and Operator.run_condition:
            if loop_counter % Operator.reflection_period == 0:
                try:
                    Q_width = float(Operator.na_fc)/Operator.transmission_Q
                    Operator.na_reflection_span = str(Q_width*Operator.na_reflection_Q_widths)
                    GUI.na_span_tile.set_value(float(Operator.na_reflection_span))
                    f0_refl,Q_refl,beta = log_reflection_scan(np.float64(Operator.na_fc), np.float64(Operator.na_reflection_span)/2)
                    GUI.beta_tile.set_value(beta)
                    GUI.message_tile.text="Reflection:"+str(timestamp)
                    GUI.update_ui(term)
                #except (TypeError, ZeroDivisionError):
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    log_error(timestamp,repr(e))
                    GUI.message_tile.text="Reflection fail:"+str(timestamp)
                    #GUI.error_tile.text=repr(e)
                    GUI.error_tile.text=(repr(e) + "-- line No. " + str(exc_tb.tb_lineno))
                    GUI.update_ui(term)
        
        #Digitizing:
        timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
        if Operator.digitization_period != 0 and Operator.run_condition:
            if loop_counter % Operator.digitization_period == 0:
                try:
                    lo_set_freq = int(float(Operator.na_fc)*1e9*100)/100 #Set the frequency to a resolution of a hundredth of a Hz. Higher precision is rejected by the LO.
                    lo_freq = set_lo_center_freq(lo_set_freq)
                    start_digitization(30)
                    GUI.message_tile.text = "Digitizing at fc = " + str(lo_freq)
                    GUI.update_ui(term)
                    finish_timestamp, freqs, pows = wait_for_digitization(return_digitization=True)
                    GUI.message_tile.text = "Digitization complete at " + str(finish_timestamp)
                    GUI.update_ui(term)
                    log_digitization(timestamp, freqs, pows) #I would rather log the start timestamp rather than the finish timestamp
                except Exception as e:
                    log_error(timestamp, repr(e))
                    GUI.error_tile.text="digitizing: " + str(timestamp)[0:19] + ": " + repr(e)
                    GUI.update_ui(term)

        #This tuning method uses a fixed increment
        #Cavity Tuning:
        timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
        if Operator.tuning_period != 0 and Operator.run_condition and Operator.dl_cm != 0 and Operator.cavity_length < Operator.max_cavity_length and Operator.cavity_length > Operator.min_cavity_length:
            if loop_counter % Operator.tuning_period == 0:
                try:
                    GUI.message_tile.text="starting tuning operation " + str(Operator.dl_cm)
                    l_cm = Operator.cavity_length
                    GUI.update_ui(term)
                    coordinated_motion(Operator.dl_cm)
                    true_dl_cm = int(steps_per_cm*Operator.dl_cm)/steps_per_cm #Account for the fact that steps are integers and can't achieve exact precision in centimeters
                    Operator.cavity_length = Operator.cavity_length + true_dl_cm
                    GUI.cavity_length_tile.set_value(Operator.cavity_length)
                    GUI.message_tile.text="done with tuning operation"
                    GUI.update_ui(term)
                    with open('cavity_current_length.txt','w') as output:
                        output.write(str(Operator.cavity_length))
                    log_cavity_params("cavity_length_cm", timestamp, Operator.cavity_length)
                except Exception as e:
                    log_error(timestamp, repr(e))
                    GUI.error_tile.text="tuning: " + str(timestamp)[0:19] + ": " + repr(e)
                    GUI.update_ui(term)

        
        #This tuning method uses a list of values
#        #Cavity Tuning:
#        timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
#        if Operator.tuning_period != 0 and Operator.run_condition:
#            if loop_counter % Operator.tuning_period == 0:
#                try:
#                    GUI.message_tile.text="starting tuning operation " + str(Operator.dl_cm)
#                    l_cm = Operator.cavity_length
#                    dl_cm = cavity_lengths_array[tuning_index]-l_cm  
#                    GUI.dl_cm_tile.set_value(dl_cm)
#                    time.sleep(1)
#                    GUI.update_ui(term)
#                    coordinated_motion(Operator.dl_cm)
#                    Operator.cavity_length = Operator.cavity_length + dl_cm
#                    GUI.cavity_length_tile.set_value(Operator.cavity_length)
#                    GUI.message_tile.text="done with tuning operation"
#                    GUI.update_ui(term)
#                    with open('cavity_current_length.txt','w') as output:
#                        output.write(str(Operator.cavity_length))
#                    #Determine the direction of tuning. The data taking is set up to scan and re-scan back and forth through the array of cavity lengths.
#                    if tune_forward:
#                        tuning_index = tuning_index + 1
#                    else:
#                        tuning_index = tuning_index - 1
#                    if tuning_index == 0:
#                        tune_forward = True
#                        GUI.tuning_mode_tile.text="Tuning Forward"
#                    if tuning_index == len(cavity_lengths_array)-1:
#                        tune_forward = False
#                        GUI.tuning_mode_tile.text="Tuning Backward"
#                    time.sleep(3)
#                    log_cavity_params("cavity_length_cm", timestamp, Operator.cavity_length)
#                except Exception as e:
#                    log_error(timestamp, repr(e))
#                    GUI.error_tile.text="tuning: " + str(timestamp)[0:19] + ": " + repr(e)
#                    GUI.update_ui(term)

        time.sleep(0.5)
        loop_counter = loop_counter+1
        
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
                    if input_str=="pause":
                        GUI.message_tile.text="Operator pausing..."
                        exec("Operator.pause=True")
                    if input_str=="resume":
                        GUI.message_tile.text="Operator resuming..."
                        exec("Operator.pause=False")
                    if input_str=="quit":
                        exec("Operator.run_condition=False")
                        exec("Operator.pause=False") #If you don't do this then it can be stuck in the pause loop and never quit
                        GUI.message_tile.text="Operator Shutting Down..."
                        while internal_thread.is_alive():
                            GUI.message_tile.text="|Operator Shutting Down...|"
                            GUI.update_ui(term)
                            time.sleep(.3)
                            GUI.message_tile.text=r'\Operator Shutting Down...'+'\\'
                            GUI.update_ui(term)
                            time.sleep(.3)
                            GUI.message_tile.text="-Operator Shutting Down...-"
                            GUI.update_ui(term)
                            time.sleep(.3)
                            GUI.message_tile.text="/Operator Shutting Down.../"
                            GUI.update_ui(term)
                            time.sleep(.3)
                            GUI.message_tile.text="-Operator Shutting Down...-"
                            GUI.update_ui(term)
                            time.sleep(.3)
                        GUI.message_tile.text="Operator has shut down. Closing GUI."
                        GUI.update_ui(term)
                        time.sleep(1)
                        break
                    else:
                        entity_str = input_str[0:input_str.find(',')]
                        val_str = input_str[(input_str.find(',')+1):]
                        #Catalogue of entities:
                        catalogue = np.asarray(["na_power", "na_fc", "na_span", "dl_cm", "transmission_period", "reflection_period", 
                                                "tuning_period", "digitization_period","max_cavity_length", "min_cavity_length",
                                                "na_transmission_Q_widths", "na_reflection_Q_widths"])
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
os.system('clear')
