import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('/home/jsinnis/GitHub/orpheus_data_taking/containerized_data_taking/'))))

from monitoring_functions import log_hall_sensors
import time

while True:
    log_hall_sensors()
    time.sleep(0.5)
