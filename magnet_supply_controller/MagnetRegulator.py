import threading
from PrologixGPIBConnection import *
from Instruments import *
import time
import copy
import yaml

#this class is the thread that regulates the magnet
#Rule: any function that starts with a "_" is not thread safe
class MagnetRegulator:
    def __init__(self, config_file_name):
        with open(config_file_name, 'r') as file:
            config = yaml.safe_load(file)
        self.prologix_ip=config["prologix_ip"]
        self.power_supply_gpib_address=config["power_supply_gpib_address"]
        self.voltmeter_gpib_address=config["voltmeter_gpib_address"]
        self.connection=PrologixGPIBConnection(self.prologix_ip)
        self.powerSupply=PowerSupply(self.connection,self.power_supply_gpib_address)
        self.voltmeter=Voltmeter(self.connection,self.voltmeter_gpib_address)

        #physics calibration values
        self.current_resistor_calibration_ohms=config["current_resistor_calibration_ohms"]

        #last read values
        self.last_voltmeter_voltage=0
        self.last_voltmeter_voltage_lock=threading.Lock()
        self.dt=0.1 #time since last loop

        #threading stuff
        self.thread = threading.Thread(target=self._thread_loop)
        self.thread.daemon = True
        self.should_quit = False

        #timing stuff
        self.loop_time=0.1 #seconds per loop
        self.last_time=time.time() #this is the time in seconds

    def read_voltmeter_voltage(self):
        voltage=self.voltmeter.get_voltage()
        with self.last_voltmeter_voltage_lock:
            self.last_voltmeter_voltage=voltage

    def get_last_voltmeter_voltage(self):
        with self.last_voltmeter_voltage_lock:
            return self.last_voltmeter_voltage
        
    def get_last_current_measurement(self):
        return self.get_last_voltmeter_voltage()/self.current_resistor_calibration_ohms
        

    def get_status_string(self):
        status_string=""
        status_string+="Vread: {}".format(self.get_last_voltmeter_voltage())
        return status_string


    def connect(self):
        try:
            self.connection.connect()
            print("configuring power supply")
            self.powerSupply.configure()
            print("configuring voltmeter")
            self.voltmeter.configure()
        except TimeoutError as e:
            print("connection timed out")
        except OSError as e:
            print("unable to connect to the prologix controller at ip address {}".format(self.prologix_ip))
            print(e)
            exit()

    def start_thread(self):
         if self.thread is not None:
            self.thread.start()

    def _thread_loop(self):
        self.connect()
        while not self.should_quit:
            try:
                ##get the voltage on the voltmeter
                self.read_voltmeter_voltage()

                ##update the PID loop
                self.dt=time.time()-self.last_time

                ##decide if I have a panic condition
                ##set the voltage on the power supply

                #sleep until next loop
                self.last_time=time.time()
                sleep_time=self.loop_time-self.last_time
                if sleep_time>0:
                    time.sleep(sleep_time)
            except TimeoutError as e:
                print("timed out on request: {}".format(e))
                print("reconnecting")
                self.connect()
        #clean up
        self.disconnect()
            
