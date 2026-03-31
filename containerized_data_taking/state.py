import threading
import json

with open('data/experiment_params.json', 'r') as f:
    state_attributes = json.load(f)

class ExperimentState:
    def __init__(self):
        self.lock = threading.Lock()

        # control flags
        self.run_condition = True
        self.pause = True

        #status flag
        self.run_status = True
        self.last_task = "Welcome to Orpheus Data Taking"
        self.error_msg = "none"

        # variables currently in Operator
        self.na_fc = state_attributes["na_fc"] 
        self.na_span = state_attributes["na_span"]
        self.transmission_Q = state_attributes["transmission_Q"]
        self.transmission_f0 = state_attributes["transmission_f0"]
        self.beta = state_attributes["beta"]
        self.dl_cm = state_attributes["dl_cm"]
        self.cavity_length = state_attributes["cavity_length"]
        self.min_cavity_length = state_attributes["min_cavity_length"]
        self.max_cavity_length = state_attributes["max_cavity_length"]
        self.na_transmission_Q_widths = state_attributes["na_transmission_Q_widths"]
        self.na_reflection_Q_widths = state_attributes["na_reflection_Q_widths"]
        self.transmission_period = state_attributes["transmission_period"]
        self.reflection_period = state_attributes["reflection_period"]
        self.tuning_period = state_attributes["tuning_period"]
        self.digitization_period = state_attributes["digitization_period"]
        self.widescan_period = state_attributes["widescan_period"]
        
    
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
                "cavity_length": self.cavity_length,
                "min_cavity_length": self.min_cavity_length,
                "max_cavity_length": self.max_cavity_length,
                "na_transmission_Q_widths": self.na_transmission_Q_widths,
                "na_reflection_Q_widths": self.na_reflection_Q_widths,
                "transmission_period": self.transmission_period,
                "reflection_period": self.reflection_period,
                "tuning_period": self.tuning_period,
                "digitization_period": self.digitization_period,
                "widescan_period": self.widescan_period
            }

    def update_json(self):
        with open('data/experiment_params.json', 'r') as f:
            data = json.load(f)
            data["na_fc"] = self.na_fc
            data["na_span"] = self.na_span
            data["transmission_Q"] = self.transmission_Q
            data["transmission_f0"] = self.transmission_f0
            data["beta"] = self.beta
            data["dl_cm"] = self.dl_cm
            data["cavity_length"] = self.cavity_length
            data["min_cavity_length"] = self.min_cavity_length
            data["max_cavity_length"] = self.max_cavity_length
            data["na_transmission_Q_widths"] = self.na_transmission_Q_widths
            data["na_reflection_Q_widths"] = self.na_reflection_Q_widths
            data["transmission_period"] = self.transmission_period
            data["reflection_period"] = self.reflection_period
            data["tuning_period"] = self.tuning_period
            data["digitization_period"] = self.digitization_period
            data["widescan_period"] = self.widescan_period
        with open('data/experiment_params.json', 'w') as f:
            json.dump(data, f, indent=4)

state = ExperimentState()
