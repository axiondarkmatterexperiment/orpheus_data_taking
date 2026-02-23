#This script is to monitor the magnet continuously while we are testing it
import time
import datetime
#from monitoring_functions import monitor_experiment, log_error, establish_databases
from monitoring_functions import log_hall_sensors, log_error, establish_databases

print('establishing databases')
establish_databases()
print('databases established')

while True:
    try:
        #monitor_experiment()
        log_hall_sensors()
    except Exception as err:
        err= str(err)
        timestamp = datetime.datetime.now()
        log_error(timestamp, err)
        print(err)
        time.sleep(1)



    time.sleep(1)
