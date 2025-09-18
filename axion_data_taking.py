#The order for every single data cycle is:
# 1. Transmission scan
# 2. Reflection scan
# 3. Update LO frequency
# 4. Digitize
# 5. Tune
#
# There are also widescans but they can be taken less frequently. Maybe every 10 cycles.

from monitoring_functions import *

all_data_taking_conditions=True #These are basic checks to make sure I am not breaking anything by turning the rods 
while all_data_taking_conditions=True:
    log_transmission_scan()
    log_reflection_scan()
    set_lo_frequency()
    digitize()
    tune_f0()
