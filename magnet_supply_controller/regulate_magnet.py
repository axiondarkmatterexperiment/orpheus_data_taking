from MagnetRegulator import *
from select import select
import sys

config_file_name="magnet_regulator_config.yaml"

#create regulator object
regulator=MagnetRegulator(config_file_name)

#TODO initial settings

#start the thread
regulator.start_thread()

report_interval=0.1
while True:
    time.sleep(report_interval)
    print(regulator.get_status_string())
    dr,dw,de = select([sys.stdin], [], [], 0)
    if dr != []:
        break
regulator.should_quit=True