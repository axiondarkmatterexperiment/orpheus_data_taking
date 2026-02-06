from data_taking_functions import log_transmission_scan
from fitting_functions import cavity_length_from_f0
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


