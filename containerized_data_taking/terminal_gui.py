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
    #internal_thread = threading.Thread(target=take_data, args=("data_taker",))
    #internal_thread.start()
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        GUI.initialize_ui()
        GUI.update_ui(term)
        while True:
            GUI.message_tile.text="yo"
            GUI.update_ui(term)
            time.sleep(0.1)
            GUI.message_tile.text="yooo"
            GUI.update_ui(term)
            time.sleep(0.1)
            val=term.inkey(timeout=0.1)
            if val:
                if val.name=="KEY_ENTER":
                    input_str=GUI.input_tile.text
                    GUI.input_tile.text=""
                    if input_str=="pause":
                        GUI.message_tile.text="Experiment pausing..."
                        #exec("Operator.pause=True")
                        requests.post("http://localhost:8000/set",
                                      json={"pause": "True"}
                                      )

                    if input_str=="resume":
                        GUI.message_tile.text="Experiment resuming..."
                        #exec("Operator.pause=False")
                        requests.post("http://localhost:8000/set",
                                      json={"pause": "False"}
                                      )
                        
                    if input_str=="quit":
                        #exec("Operator.run_condition=False")
                        requests.post("http://localhost:8000/set",
                                      json={"run_condition": "False"}
                                      )
                        #exec("Operator.pause=False") #If you don't do this then it can be stuck in the pause loop and never quit
                        requests.post("http://localhost:8000/set",
                                      json={"pause": "False"}
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
                        val_str = input_str[(input_str.find(',')+1):]
                        #Catalogue of entities:
                        catalogue = np.asarray(["na_power", "na_fc", "na_span", "dl_cm", "transmission_period", "reflection_period", 
                                                "tuning_period", "digitization_period","max_cavity_length", "min_cavity_length",
                                                "na_transmission_Q_widths", "na_reflection_Q_widths"])
                        cat_idx = np.argwhere(catalogue==entity_str)
                        #If an item in the catalogue has been selected, update the DAQ variable, which is always a string
                        if np.size(cat_idx)>0:
                            #exec("Operator."+entity_str+"="+val_str)
                            requests.post("http://localhost:8000/set",
                                      json={entity_str: val_str}
                                      )
                            #status = requests.get("http://localhost:8000/status").json()
                            #exec("GUI."+entity_str+"_tile.set_value(Operator."+entity_str+")")
                else:
                    GUI.input_tile.handle_key(val)
                GUI.update_ui(term)
    term.exit_fullscreen()

run_GUI()
os.system('clear')
