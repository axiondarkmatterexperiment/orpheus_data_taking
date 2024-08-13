from PrologixGPIBConnection import PrologixGPIBConnection

class PowerSupply: # Agilent E3631A
    def __init__(self,connection,gpib_address):
        self.connection=connection
        self.gpib_address=gpib_address

    def configure(self):
        #configures the power supply the way I want it to be configured
        #TODO implement this
        #self.set_voltage(0)
        return True
        
    def set_voltage(self,voltage):
        #example: APPL P6V, 3.0, 1.0 #+6V supply to 3V rated at 1A

        #set voltage in volts
        command="APPL P6V, {}, 0.1".format(voltage)
        self.connection.send_message(self.gpib_address,command) #this may not be the right command
        #get the voltage to verify
        return self.get_voltage()
    
    def get_voltage(self):
        #example 
        command="SOUR:VOLT?"
        self.connection.send_message(self.gpib_address,command) #this may not be the right command
        return float(self.connection.read().decode())

    def on_off(self,on):
        if on:
            self.connection.send_message(self.gpib_address,"OUTP ON") #this may not be the right command
        else:
            self.connection.send_message(self.gpib_address,"OUTP OFF") #    this may not be the right command
        return self.get_on_off()
    


class Voltmeter: # Fluke 8840A
    def __init__(self,connection,gpib_address):
        self.connection=connection
        self.gpib_address=gpib_address

    def configure(self):
        #F1 VDC
        #R1 200 mV range (2= 2V, 3=20 V)
        #S0 slow sample rate
        #T2 - trigger on question mark
        #N1102P0
        self.connection.send_message(self.gpib_address,"N1102P0")
        return True
        

    def get_voltage(self):
        self.connection.send_message(self.gpib_address,"?") #this isn't the right command
        return float(self.connection.read().decode())
