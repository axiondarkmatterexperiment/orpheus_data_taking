from monitoring_functions import query_SCPI
IP_ADDRESS = "192.168.25.8"
PORT = 50000
TIMEOUT=5
timestamp, dig_status = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "GET:STATUS?\n")
print(dig_status[0:-1])

from data_taking_functions import wait_for_digitization
print('now trying wait_for_digitization function')
wait_for_digitization(return_digitization=False)
print("finished waiting")

print('now looking for frequencies')
t, f = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "GET:FREQUENCY_BINS?\n")
print(f)

