from TextUI import *
from OrpheusOperator import OrpheusOperator
import numpy as np
from blessed import Terminal
import requests

class OrpheusGUI:
    def __init__(self):
        Operator=OrpheusOperator()
        #Commands catalogue:
        self.catalogue_tile = ListTile(["na_power_trans,<>: (dBm)", "na_power_refl,<>: (dBm)", "na_fc,<>: (GHz)", "na_span,<>: (GHz)",
                                        "transmission_period,<>: ()","reflection_period,<>: ()","tuning_period,<>: ()",
                                        "max_cavity_length,<>: (cm)","min_cavity_length,<>: (cm)","na_transmission_Q_widths,<>: ()",
                                        "na_reflection_Q_widths,<>: ()"],title="Command Catalogue",rect=(0,0,65,0))
       
        self.tuning_mode_tile = TextTile("tuning forward",(0,0,35,0),title="tuning mode") 
        #input tile and message tile (on the bottom of the GUI):
        self.input_tile = TextEntryTile("",(0,0,35,4),title="command input:")
        self.message_tile = TextTile("",(0,0,65,4),title="Message")	
        self.error_tile = TextTile("",(0,0,100,4),title="Most recent error:")

        #values display:
        self.na_power_tile = ValueTile(float(Operator.na_power),(0,0,33,4),title="NA Power", units="dBm")
        self.na_fc_tile = ValueTile(float(Operator.na_fc)/1e9,(0,0,33,4),title="NA fc", units="GHz")
        self.na_span_tile = ValueTile(float(Operator.na_span)/1e9,(0,0,34,4),title="NA span", units="GHz")
        self.f0_tile = ValueTile(0,(0,0,33,4),title="f0_trans", units="GHz")
        self.Q_tile = ValueTile(0,(0,0,33,4),title="Q_trans")
        self.beta_tile = ValueTile(0,(0,0,34,4),title="beta")

        self.na_transmission_Q_widths_tile = ValueTile(0,(0,0,50,4),title="transmission Q widths")
        self.na_reflection_Q_widths_tile = ValueTile(0,(0,0,50,4),title="reflection Q widths")

        self.cavity_length_tile = ValueTile(0,(0,0,25,4),title="cavity_length", units="cm")
        self.max_cavity_length_tile = ValueTile(0,(0,0,25,4),title="max_cavity_length", units="cm")
        self.min_cavity_length_tile = ValueTile(0,(0,0,25,4),title="min_cavity_length", units="cm")
        self.dl_cm_tile = ValueTile(0,(0,0,25,4),title="dl_cm",units="cm")
         
        #Data taking period tiles:
        self.transmission_period_tile = ValueTile(Operator.transmission_period,(0,0,20,4),title="trans period")
        self.reflection_period_tile = ValueTile(Operator.reflection_period,(0,0,20,4),title="refl period")
        self.digitization_period_tile = ValueTile(Operator.digitization_period,(0,0,20,4),title="digit period")
        self.tuning_period_tile = ValueTile(Operator.tuning_period,(0,0,20,4),title="tuning period")
        self.widescan_period_tile = ValueTile(Operator.widescan_period,(0,0,20,4),title="widescan period")
        
        self.ui=VStackTile((0,0,100,52),[HStackTile((0,0,100,12),[self.tuning_mode_tile,self.catalogue_tile]),
                        HStackTile((0,0,100,4),[self.na_power_tile,
                                self.na_fc_tile,
                	       	    self.na_span_tile]),
                        HStackTile((0,0,100,4),[self.f0_tile,
                                self.Q_tile,
                	       	    self.beta_tile]),
                        HStackTile((0,0,100,4),[self.na_transmission_Q_widths_tile,
                                self.na_reflection_Q_widths_tile]),
                        HStackTile((0,0,100,4),[self.cavity_length_tile,
                                self.dl_cm_tile,
                	       	    self.max_cavity_length_tile,
                                self.min_cavity_length_tile]),
                        HStackTile((0,0,100,4),[self.transmission_period_tile,
                                self.reflection_period_tile,
                	       	    self.digitization_period_tile,
                                self.tuning_period_tile,
                                self.widescan_period_tile]),
                        HStackTile((0,0,100,4),[self.input_tile,
                                self.message_tile]),
                        HStackTile((0,0,100,4),[self.error_tile])])#,
        

    def initialize_ui(self):
        self.message_tile.text="Welcome to Orpheus data taking"

    def get_attribute(entity_str):
        url = "http://localhost:8000/get?keys=" + entity_str
        return requests.get(url).json()[entity_str]

    def update_ui(self, terminal):
        directory= dir(self)
        for item in directory:
            if item[-5:]=='_tile':
                item_str = item[0:-5] #cut off _tile at the end of it
                try:
                    val = get_attribute(item_str)
                    update_value_tile(item_str,val)
                except Exception as e:
                    pass
        self.ui.draw(terminal)

    def update_value_tile(self,entity_str,value):
        exec("self."+entity_str+"_tile.set_value("+value+")")

    def set_na_power_display(self,power):
        self.na_power_tile.set_value(power)

    #The format of the commands are all: entity,value
    def CommandBrain(self, input_str):
        #Parse the input into entity and the input value. The delimiter used is a comma.
        entity_str = input_str[0:input_str.find(',')]
        val_str = input_str[(input_str.find(',')+1):]
        #Catalogue of entities:
        catalogue = np.asarray(["na_power", "na_fc", "na_span"])
        cat_idx = np.argwhere(catalogue==entity_str)
        #If an item in the catalogue has been selected, update the DAQ variable, which is always a string
        if np.size(cat_idx)>0:
            exec("Operator."+entity_str+"="+val_str)
