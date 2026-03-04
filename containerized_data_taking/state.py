import threading
with open('cavity_current_length.txt', 'r', encoding='utf-8') as f:
    cavity_length = float(f.read())

class ExperimentState:
    def __init__(self):
        self.lock = threading.Lock()

        # control flags
        self.run_condition = True
        self.pause = False

        #status flag
        self.run_status = True
        self.last_task = "Welcome to Orpheus Data Taking"
        self.error_msg = "none"

        # variables currently in Operator
        self.na_fc = 16.605
        self.na_span = 0.05
        self.transmission_Q = 2000
        self.transmission_f0 = 16.605
        self.beta = 0.5
        self.dl_cm = 0
        self.transmission_period = 0
        self.reflection_period = 0
        self.tuning_period = 0
        self.digitization_period = 0
        self.cavity_length = cavity_length
        self.max_cavity_length = 17
        self.min_cavity_length = 13
        self.na_transmission_Q_widths = 10
        self.na_reflection_Q_widths = 5
    
    def to_dict(self):
        return {
                "run_condition": self.run_condition,
                "pause": self.pause,
                "run_status": self.run_status,
                "last_task": self.last_task,
                "error_msg": self.error_msg,
                "na_fc": self.na_fc,
                "na_span": self.na_span,
                "transmission_Q": self.transmission_Q,
                "transmission_f0": self.transmission_f0,
                "beta": self.beta,
                "dl_cm": self.dl_cm,
                "transmission_period": self.transmission_period,
                "reflection_period": self.reflection_period,
                "tuning_period": self.tuning_period,
                "digitization_period": self.digitization_period,
                "cavity_length": self.cavity_length,
                "max_cavity_length": self.max_cavity_length,
                "min_cavity_length": self.min_cavity_length,
                "na_transmission_Q_widths": self.na_transmission_Q_widths,
                "na_reflection_Q_widths": self.na_reflection_Q_widths
            }
            

state = ExperimentState()
