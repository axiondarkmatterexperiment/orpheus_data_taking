from typing import Any
import PrologixGPIBConnection

class PowerSupply:
    def __init__(self,connection,gpib_address):
        self.connection=connection
        self.gpib_address=gpib_address

    def configure(self):
        #configures the power supply the way I want it to be configured
        ... #TODO implement this

    def set_voltage(self,voltage):
        #set voltage in volts
        self.connection.send_message(self.gpib_address,"VOLT {}".format(voltage)) #this may not be the right command
        #get the voltage to verify
        return self.get_voltage()
    
    def get_voltage(self):
        self.connection.send_message(self.gpib_address,"VOLT?") #this may not be the right command
        return float(self.connection.read().decode())

    def on_off(self,on):
        if on:
            self.connection.send_message(self.gpib_address,"OUTP ON") #this may not be the right command
        else:
            self.connection.send_message(self.gpib_address,"OUTP OFF") #    this may not be the right command

class Voltmeter:
    def __init__(self,connection,gpib_address):
        self.connection=connection
        self.gpib_address=gpib_address

    def configure(self):
        self.connection.send_message(self.gpib_address,"CONF:VOLT:DC") #this isn't the right command

    def get_voltage(self):
        self.connection.send_message(self.gpib_address,"MEAS:VOLT?") #this isn't the right command
        return float(self.connection.read().decode())