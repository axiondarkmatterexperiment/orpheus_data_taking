#This class will hold all of the DAQ variables
from monitoring_functions import *

class OrpheusOperator:
    def __init__(self):
        VNA_IP = "192.168.25.7"

        VNA_PORT=5025

        VNA_TIMEOUT=10
        #Begin with a true run condition
        self.run_condition=True
        self.pause=False
        self.max_cavity_length=16
        self.min_cavity_length=13.5

        #set the data taking periods to safe starting values:
        self.transmission_period = 1
        self.reflection_period = 1
        self.digitization_period = 0
        self.tuning_period = 0
        self.widescan_period=0

        #Initialize the VNA
        t_throwaway, self.na_power= query_SCPI(VNA_IP,VNA_PORT,VNA_TIMEOUT,"SOUR1:POW?\n") #Check this command is correct
        t_throwaway, fc=query_SCPI(VNA_IP,VNA_PORT,VNA_TIMEOUT,"SENS1:FREQ:CENT?\n") #Check this command is correct
        t_throwaway, span=query_SCPI(VNA_IP,VNA_PORT,VNA_TIMEOUT,"SENS1:FREQ:SPAN?\n") #Check this command is correct
        
        self.na_fc = str(float(fc)/1e9) #The units for fc is GHz
        self.na_span = str(float(span)/1e9)
        self.na_transmission_span = str(float(span)/1e9) #The units for span is GHz
        self.na_reflection_span = str(float(span)/2e9) #The reflection fitting usually benefits from narrower windows.

        self.transmission_Q=4000
        self.na_transmission_Q_widths=8
        self.na_reflection_Q_widths=4

        #Initialize the motor variables
        self.dl_cm = 0.0
        self.cavity_length = 15.6
