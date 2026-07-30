import time
from data_taking_functions import *

#start_time = time.perf_counter()
#x,y = log_transmission_scan(16.627,0.05)
##log_transmission_widescan(15.5,17.2)
#end_time = time.perf_counter()
#runtime = round((end_time - start_time), 2)
#print(f'Runtime: {runtime} seconds')



f_center_GHz = 16.627
f_span_GHz = 0.05
n_avgs = 16
if_bw_Hz = 1e4
na_power=-10

#send the query to the VNA:
IP_ADDRESS="192.168.25.7"
PORT=5025
TIMEOUT=60 #This might need to be changed dependent on the averaging time

very_start_time = time.perf_counter()

start_time = time.perf_counter()
query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "ABOR; INIT1:CONT OFF;*OPC?\n")
end_time = time.perf_counter()
runtime = round((end_time - start_time),2)
print(f"Line No: {sys._getframe().f_lineno}")
print(f"time elapsed in halting VNA initial condition = {runtime} seconds")

#Sweep setup
start_time = time.perf_counter()
SCPI_string = "SENS1:FREQ:CENT " + str(f_center_GHz*1e9) + ";*OPC?\n"
query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
SCPI_string = "SENS1:FREQ:SPAN " + str(f_span_GHz*1e9) + ";*OPC?\n"
query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
SCPI_string = "SOUR:POW " + str(na_power) + ";*OPC?\n"
query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
end_time = time.perf_counter()
runtime = round((end_time - start_time),2)
print(f"Line No: {sys._getframe().f_lineno}")
print(f"time elapsed in setting frequency window and na power = {runtime} seconds")

#Averaging
start_time = time.perf_counter()
SCPI_string = "SENS1:AVER:COUNT " + str(n_avgs) + ";*OPC?\n"
query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
SCPI_string = "TRIG:AVER ON;*OPC?\n"
query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
#I commented the following two lines because it took forever
SCPI_string = "TRIG:AVER:CLE;*OPC?\n"#Clears and restarts the averaging of the measurement data
query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
SCPI_string = "SENS1:BAND " + str(if_bw_Hz) + ";*OPC?\n"
query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
end_time = time.perf_counter()
runtime = round((end_time - start_time),2)
print(f"Line No: {sys._getframe().f_lineno}")
print(f"time elapsed in averaging settings = {runtime} seconds")

#Request expected scan duration:
start_time = time.perf_counter()
SCPI_string = "SENS1:SWE:TIME?\n"
throwaway_timestamp, sweep_duration = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
timedelta_duration = datetime.timedelta(seconds=float(sweep_duration)*n_avgs)
end_time = time.perf_counter()
runtime = round((end_time - start_time),2)
print(f"Line No: {sys._getframe().f_lineno}")
print(f"time elapsed in calculating expected scan time = {runtime} seconds")

#Triggering
start_time = time.perf_counter()
SCPI_string = "INIT1;*OPC?\n" #sets trigger to single
query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
SCPI_string = "TRIG:SOUR BUS;*OPC?\n" #sets trigger source to bus
query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
SCPI_string = "TRIG;*OPC?\n" #triggers the measurement
query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
end_time = time.perf_counter()
runtime = round((end_time - start_time),2)
print(f"Line No: {sys._getframe().f_lineno}")
print(f"time elapsed in setting trigger and triggering = {runtime} seconds")

#Wait for measurement to finish
t1 = datetime.datetime.now(pytz.timezone('US/Pacific'))
t2 = datetime.datetime.now(pytz.timezone('US/Pacific'))
print('waiting for ' + str(timedelta_duration))
while t2-t1 < timedelta_duration:
    t2 = datetime.datetime.now(pytz.timezone('US/Pacific'))
    time.sleep(0.1)

#Take scan data
start_time = time.perf_counter()
SCPI_string = "CALC1:DATA:SDAT?\n" #ask for the IQ data. Format: n*2-1 is real, n*2 is imaginary
timestamp, iq_raw = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)

SCPI_string = "SENS1:FREQ:DATA?\n" #ask for the frequency vector
timestamp, f_raw = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
end_time = time.perf_counter()
runtime = round((end_time - start_time),2)
print(f"Line No: {sys._getframe().f_lineno}")
print(f"time elapsed in retrieving scan from VNA = {runtime} seconds")

total_runtime = round((end_time - very_start_time),2)
print(f"total script runtime = {total_runtime} seconds")
