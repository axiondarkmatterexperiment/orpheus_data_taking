from MagnetRegulator import *

#this simulates the magnet so we can test the regulator
class FakeMagnetRegulator(MagnetRegulator):
    def __init__(self,config_file_name):
        super().__init__(config_file_name)
        #physics simulation stuff
        self.last_sim_update=time.time()
        self.current=0

        self.current_resistor_ohms=3e-6
        self.line_resistance_ohms=0.1
        self.inductance_henries=5.0

        #uncertainties
        self.voltage_measure_uncertainty=0.01


    def connect(self):
        pass

    def disconnect(self):
        pass

    def read_voltmeter_voltage(self):
        self.update_sim()
        with self.last_voltmeter_voltage_lock:
            self.last_voltmeter_voltage=self.current*self.current_resistor_ohms

    def set_power_supply_voltage(self,voltage):
        with self.last_ps_voltage_lock:
            #TODO limits
            self.last_ps_voltage=voltage
            return  voltage

    def update_sim(self):
        #simulate the magnet
        with self.last_ps_voltage_lock:
            v=self.last_ps_voltage
        dt=time.time()-self.last_sim_update
        dI_dt=(v-self.current*self.current_resistor_ohms-self.current*self.line_resistance_ohms)/self.inductance_henries
        self.current+=dI_dt*dt
        self.last_sim_update=time.time()