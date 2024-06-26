#This script is to monitor the magnet continuously while we are testing it
import time
from monitoring_functions import log_magnet_temps, log_LHe_level

while True:
    log_magnet_temps()
    log_LHe_level()
    time.sleep(5)