#This class will hold all of the DAQ variables
from monitoring_functions import *

class OrpheusOperator:
    def __init__(self):
        VNA_IP = "192.168.25.7"

        VNA_PORT=5025

        VNA_TIMEOUT=10

        #Initialize the VNA
        t_throwaway, self.na_power= query_SCPI(VNA_IP,VNA_PORT,VNA_TIMEOUT,"SOUR1:POW?\n") #Check this command is correct
        t_throwaway, fc=query_SCPI(VNA_IP,VNA_PORT,VNA_TIMEOUT,"SENS1:FREQ:CENT?\n") #Check this command is correct
        t_throwaway, span=query_SCPI(VNA_IP,VNA_PORT,VNA_TIMEOUT,"SENS1:FREQ:SPAN?\n") #Check this command is correct
        
        self.na_fc = str(float(fc)/1e9) #The units for fc is GHz
        self.na_span = str(float(span)/1e9) #The units for span is GHz
