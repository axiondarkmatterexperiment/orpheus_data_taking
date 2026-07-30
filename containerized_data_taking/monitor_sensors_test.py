
from monitoring_functions import log_hall_sensors
import time

while True:
    log_hall_sensors()
    time.sleep(0.5)
