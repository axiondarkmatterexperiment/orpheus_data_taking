from data_taking_functions import log_transmission_scan
from fitting_functions import cavity_length_from_f0
import numpy as np
f_center_GHz = input("input the current f0 in GHz: ")
f_center_GHz = float(f_center_GHz)
f_span_GHz = input("input the na f_span_GHz you want in GHz: ")
f_span_GHz = float(f_span_GHz)

print("f_center_GHz is "+str(f_center_GHz)+"GHz")
print("f_span_GHz is "+str(f_span_GHz)+"GHz")
ok = input("are these values ok? Hit enter if so, otherwise, type anything then hit enter.")

if ok=="":
    f0,Q = log_transmission_scan(f_center_GHz,f_span_GHz)
    f0,Q = log_transmission_scan(f0/1e9,f_span_GHz)

    f0_GHz = f0/1e9
    length_cm = cavity_length_from_f0(f0_GHz)
    print("the measured f0 is " + str(f0_GHz) + "GHz")
    print("the calculated cavity length is " + str(length_cm) + "cm")
    ok2 = input("are these values ok? Hit enter if so, otherwise, type anything then hit enter. If OK, the value will be saved to cavity_current_length.txt")
    if ok2=="":
        np.savetxt("cavity_current_length.txt",np.asarray([length_cm]))
    else:
        print("Doing nothing. The cavity_current_length.txt file remains unchanged.")
