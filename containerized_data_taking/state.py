# state.py
# Written by ChatGPT
import threading

class ExperimentState:
    def __init__(self):
        self.lock = threading.Lock()

        # control flags
        self.run_condition = True
        self.pause = False

        #status flag
        self.run_status = True

        # variables currently in Operator
        self.na_fc = 16.605*1e9 
        self.na_span = 0.05*1e9
        self.dl_cm = 0
        self.transmission_period = 1
        self.reflection_period = 0
        self.tuning_period = 0
        self.digitization_period = 0
        self.max_cavity_length = 0
        self.min_cavity_length = 0
        self.na_transmission_Q_widths = 0
        self.na_reflection_Q_widths = 0

state = ExperimentState()
