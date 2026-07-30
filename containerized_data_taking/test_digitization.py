from data_taking_functions import *
from datetime import datetime as dt
while True:
    start_timestamp = dt.now(pytz.timezone('US/Pacific'))
    start_digitization(30)
    finish_timestamp, freqs, pows, = wait_for_digitization(return_digitization=True)
    pows=pows[0:-1] #Removing the NaN value which is always at the end for some reason
    freqs=freqs[0:-1]
    log_digitization(start_timestamp, freqs, pows)
    print(start_timestamp)
