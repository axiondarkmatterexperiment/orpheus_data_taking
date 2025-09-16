##########################################################################################################
###                                                                                                    ###
### This script runs the Orpheus data taking and sets up an interactive and self-updating GUI          ###
### that reports the status of the experiment to a remote or local operator. You do not need           ###
### to SSH into the orpheus computer to run it, but you need to be connected to the CENPA network      ###
### either through ethernet or VPN.  -Jimmy                                                            ###
###                                                                                                    ###
##########################################################################################################


from blessed import Terminal
from OrpheusGUI import OrpheusGUI#, CommandBrain
from OrpheusOperator import OrpheusOperator
#from data_taking_functions import log_transmission_scan, log_reflection_scan, tune_cavity, digitize
from monitoring_functions import *
from data_taking_functions import log_transmission_scan, log_reflection_scan
import datetime
import pytz
import time
import numpy as np
import TextUI
import threading

term = Terminal()
GUI=OrpheusGUI()
Operator=OrpheusOperator()

def run_GUI(name):
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
                        break
                    else:
                        entity_str = input_str[0:input_str.find(',')]
                        val_str = input_str[(input_str.find(',')+1):]
                        #Catalogue of entities:
                        catalogue = np.asarray(["na_power", "na_fc", "na_span"])
                        cat_idx = np.argwhere(catalogue==entity_str)
                        #If an item in the catalogue has been selected, update the DAQ variable, which is always a string
                        if np.size(cat_idx)>0:
                            exec("Operator."+entity_str+"="+val_str)
                            exec("GUI."+entity_str+"_tile.set_value("+val_str+")")
                else:
                    GUI.input_tile.handle_key(val)
                GUI.update_ui(term)
    term.exit_fullscreen()

#This is to run the full data taking cadence, which is separate from logging the sensor values
def take_data(name):
    #Count the loops to have differing periods for different actions
    loop_counter = 0
    
    while True:
        #
        #NA scans
        timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
        try:
            GUI.na_fc_tile.set_value(float(Operator.na_fc))
            GUI.na_span_tile.set_value(float(Operator.na_span))
            GUI.update_ui(term)
            f0,Q = log_transmission_scan(np.float64(Operator.na_fc), np.float64(Operator.na_span))
            #Q_width = f0/Q
            #Operator.na_span = str(Q_width*Operator.na_Q_widths)
            Operator.na_fc = str(f0/1e9)
            f0_refl,Q_refl,beta = log_reflection_scan(np.float64(Operator.na_fc), np.float64(Operator.na_span))
            GUI.beta_tile.set_value(beta)
            GUI.Q_tile.set_value(Q)
            GUI.f0_tile.set_value(f0/1e9)
            GUI.message_tile.text="scan:"+str(timestamp)
            GUI.update_ui(term)
        except (TypeError, ZeroDivisionError):
            GUI.message_tile.text="fail:"+str(timestamp)
            GUI.update_ui(term)
        #log_reflection_scan(np.float64(Operator.na_fc), np.float64(Operator.na_span))
        
        #We should also display the latest fit values: GUI.Q_tile

        #Digitize Gray will inform me about this later
        #digitize(f0,dig_span,

        #Tune f0:
        #tune_cavity()

        #Widescan every 20 cycles:
        #if loop_counter%20==0:
            #log_transmission_scan(np.float64(Operator.widescan_fc), np.float64(Operator.widescan_span), np.float64(Operator.widescan_power), np.float64(Operator.widescan_N_avgs))
        
        loop_counter = loop_counter+1
        

def sensor_monitoring(name):
    while True:
        log_sensors()#different from log_sensor()

establish_databases()
thread1 = threading.Thread(target=run_GUI, args=("GUI_runner",))
thread2 = threading.Thread(target=take_data, args=("data_taker",))
#thread3 = threading.Thread(target=take_data, args=("sensor_monitor",))

thread1.start()
thread2.start()
#thread3.start()
