##########################################################################################################
###                                                                                                    ###
###         This is the code for the GUI which interfaces with the experiment thru an API              ###
###                                                                                                    ###
##########################################################################################################

from blessed import Terminal
from OrpheusGUI import OrpheusGUI
import datetime
import pytz
import time
import sys
import os
import TextUI
import threading
import requests
from monitoring_functions import *

term = Terminal()
GUI=OrpheusGUI()

def get_attribute(entity_str):
    url = "http://localhost:8000/get?keys=" + entity_str
    return requests.get(url).json()[entity_str]

def run_GUI():
    establish_databases()
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        GUI.initialize_ui()
        GUI.update_ui(term)
        loop_counter=0
        while True:
            #if loop_counter%10==0: #If I do it every time it slows down the GUI significantly
            GUI.update_all_tiles(term)
            val=term.inkey(timeout=0.1)
            if val:
                if val.name=="KEY_ENTER":
                    input_str=GUI.input_tile.text
                    GUI.input_tile.text=""
                    if input_str=="pause":
                        GUI.message_tile.text="Experiment pausing..."
                        requests.post("http://localhost:8000/set",
                                      json={"pause": True}
                                      )

                    elif input_str=="resume":
                        GUI.message_tile.text="Experiment resuming..."
                        requests.post("http://localhost:8000/set",
                                      json={"pause": False}
                                      )

                    elif input_str=="exit":
                        GUI.message_tile.text="Closing GUI, leaving experiment as is..."
                        GUI.update_ui(term)
                        time.sleep(1.2)
                        break

                    elif input_str=="quit":
                        requests.post("http://localhost:8000/set",
                                      json={"run_condition": False}
                                      )
                        requests.post("http://localhost:8000/set",
                                      json={"pause": False}
                                      )
                        GUI.message_tile.text="Experiment Shutting Down..."
                        run_status = get_attribute("run_status")
                        while run_status == True:
                            GUI.message_tile.text="|Experiment Shutting Down...|"
                            GUI.update_ui(term)
                            time.sleep(.3)
                            GUI.message_tile.text=r'\Experiment Shutting Down...'+'\\'
                            GUI.update_ui(term)
                            time.sleep(.3)
                            GUI.message_tile.text="-Experiment Shutting Down...-"
                            GUI.update_ui(term)
                            time.sleep(.3)
                            GUI.message_tile.text="/Experiment Shutting Down.../"
                            GUI.update_ui(term)
                            time.sleep(.3)
                            GUI.message_tile.text="-Experiment Shutting Down...-"
                            GUI.update_ui(term)
                            time.sleep(.3)
                            requests
                            run_status = get_attribute("run_status") 
                            if run_status == False:
                                break
                        GUI.message_tile.text="Experiment has shut down. Closing GUI."
                        GUI.update_ui(term)
                        time.sleep(1)
                        break
                    else:
                        entity_str = input_str[0:input_str.find(',')]
                        #Catalogue of entities:
                        catalogue = np.asarray(["na_power", "na_fc", "na_span", "transmission_Q", "dl_cm", "transmission_period", "reflection_period", 
                                                "tuning_period", "digitization_period","max_cavity_length", "min_cavity_length",
                                                "na_transmission_Q_widths", "na_reflection_Q_widths"])
                        cat_idx = np.argwhere(catalogue==entity_str)
                        #If an item in the catalogue has been selected, update the attribute of the state class through the API
                        if np.size(cat_idx)>0:
                            val_str = input_str[(input_str.find(',')+1):]
                            val=float(val_str)
                            requests.post("http://localhost:8000/set",
                                      json={entity_str: val}
                                      )
                else:
                    GUI.input_tile.handle_key(val)
                GUI.update_ui(term)
                loop_counter = loop_counter + 1
    term.exit_fullscreen()

run_GUI()
