import datetime
import pytz
from monitoring_functions import scan_na

while True:
    x,y = scan_na(15.905996,0.03)
    if y:
        print("worked: " + str(datetime.datetime.now(pytz.timezone('US/Pacific'))))
    else:
        print("error caught: " + str(datetime.datetime.now(pytz.timezone('US/Pacific'))))
