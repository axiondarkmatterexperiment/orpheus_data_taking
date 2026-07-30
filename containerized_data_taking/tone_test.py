#To run this, hook up the LO signal generator directly to the digitizer.
from data_taking_functions import set_lo_freq, set_lo_power, start_digitization, wait_for_digitization, log_digitization
from datetime import datetime as dt
import numpy as np
import pytz
import matplotlib.pyplot as plt
import time

lo_pows = np.array([-20,-15,-10,-5,0])
lo_pows = np.arange(-20,0,2,dtype=int)
atten_dB = 50 #50 dB attenuators are on the LO output for these tests
set_lo_freq(30e6)
set_lo_power(lo_pows[0])

results = np.zeros((np.size(lo_pows), 3))
i=0
for p in lo_pows:
    power_check = set_lo_power(p)
    print('SG power set to ' + str(power_check) + 'dBm.')
    time.sleep(1)
    start_timestamp = dt.now(pytz.timezone('US/Pacific'))
    print('beginning digitization...')
    start_digitization(1)
    finish_timestamp, freqs, pows = wait_for_digitization(return_digitization=True)
    pows=pows[0:-1] #Removing the NaN value which is always at the end for some reason
    freqs=freqs[0:-1]
    log_digitization(start_timestamp, freqs, pows)

    results[i,0] = p-atten_dB
    results[i,1] = np.max(pows)/(50*1e6) #50 Ohms impedance, and 1e6 to account for mV to V.
    results[i,2] = freqs[np.argmax(pows)]

    print('recorded peak height = ' + str(np.log10(np.max(pows))))
    #print('recorded peak height = ' + str((np.log10(np.max(pows))-14.886)/0.098))
    print('recorded peak height = ' + str(results[i,1]))
    print('peak found at = ' + str(freqs[np.argmax(pows)]))
    print('------------------------------------------------')
    
    i = i+1


#plt.plot(results[:,0], np.log10(results[:,1]), '.', markersize=16, label='1s acquisition time')
plt.plot(results[:,0], results[:,1], '.', markersize=16, label='1s acquisition time')
print(results)
x = results[:,0]
#y = np.log10(results[:,1])
y = results[:,1]
fit_params = np.polyfit(x,y,1)
print(fit_params)
fitted_data = fit_params[1] + (lo_pows-50)*fit_params[0]

plt.plot(lo_pows-atten_dB, fitted_data, color = 'r', label = f"{fit_params[0]}*x + {fit_params[1]}")
plt.grid()
plt.xlabel(r'SG power [dBm]')
plt.ylabel(r'Log10 of measured peak power [arb]')
plt.legend()
#plt.savefig('plots/tone_test.pdf')
plt.savefig('plots/tone_test_mV_attempt.pdf')
plt.close()

#plt.plot(results[:,0], (np.log10(results[:,1])-14.886)/0.098, '.', markersize=16, label='re-scaled to dBm')
#plt.plot(results[:,0], results[:,0], color = 'r', label = 'x=y')
#plt.grid()
#plt.xlabel(r'SG power [dBm]')
#plt.ylabel(r'Attempt at rescaling Dig Power to dBm')
#plt.legend()
#plt.savefig('plots/tone_test_rescaled.pdf')
#plt.close()

'''

set_lo_power(-20)

results = np.zeros((np.size(lo_pows), 3))
i=0
for p in lo_pows:
    set_lo_power(p)
    print('SG power set to ' + str(p) + 'dBm.')
    time.sleep(1)
    start_timestamp = dt.now(pytz.timezone('US/Pacific'))
    print('beginning digitization...')
    start_digitization(10)
    finish_timestamp, freqs, pows = wait_for_digitization(return_digitization=True)
    pows=pows[0:-1] #Removing the NaN value which is always at the end for some reason
    freqs=freqs[0:-1]
    log_digitization(start_timestamp, freqs, pows)

    results[i,0] = p-atten_dB
    results[i,1] = np.max(pows)
    results[i,2] = freqs[np.argmax(pows)]

    print('LO power = ' + str(p) + ' dBm')
    print('recorded peak height = ' + str(np.log10(np.max(pows))))
    print('peak found at = ' + str(freqs[np.argmax(pows)]))
    print('------------------------------------------------')
    
    i = i+1

plt.plot(results[:,0], np.log10(results[:,1]), '.', markersize=14, label='10s acquisition time')

set_lo_power(-20)

results = np.zeros((np.size(lo_pows), 3))
i=0
for p in lo_pows:
    set_lo_power(p)
    print('SG power set to ' + str(p) + 'dBm.')
    time.sleep(1)
    start_timestamp = dt.now(pytz.timezone('US/Pacific'))
    print('beginning digitization...')
    start_digitization(30)
    finish_timestamp, freqs, pows = wait_for_digitization(return_digitization=True)
    pows=pows[0:-1] #Removing the NaN value which is always at the end for some reason
    freqs=freqs[0:-1]
    log_digitization(start_timestamp, freqs, pows)

    results[i,0] = p-atten_dB
    results[i,1] = np.max(pows)
    results[i,2] = freqs[np.argmax(pows)]

    print('LO power = ' + str(p) + ' dBm')
    print('recorded peak height = ' + str(np.log10(np.max(pows))))
    print('peak found at = ' + str(freqs[np.argmax(pows)]))
    print('------------------------------------------------')
    
    i = i+1
plt.plot(results[:,0], np.log10(results[:,1]), '.', markersize=12, label= '30s acquisition time')
'''
