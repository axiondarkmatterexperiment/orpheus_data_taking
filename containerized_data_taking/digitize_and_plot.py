#The purpose of this is to be a simple script that you can use to test the digitizer. It defines a function which calls
#the digitizer and then saves a plot of the digitized data in different units depending on what the user wants.
from data_taking_functions import start_digitization, wait_for_digitization
import matplotlib.pyplot as plt
import numpy as np

def digitize_and_save_plot(digitization_seconds, power_units):
    start_digitization(digitization_seconds)
    finish_timestamp, freqs, pows, = wait_for_digitization(return_digitization=True)
    if power_units == 'dBm':
        plt.plot(np.array(freqs)/1e6,10*(np.log10(pows)-15))
        plt.grid()
        plt.xlabel("frequency [MHz]")
        plt.ylabel("power [approximated dBm]")
        plt.savefig('plots/digitization_test.pdf')
    elif power_units == 'raw':
        plt.plot(np.array(freqs)/1e6, pows)
        plt.grid()
        plt.xlabel("frequency [MHz]")
        plt.ylabel("power [raw digitizer units]")
        plt.savefig('plots/digitization_test.pdf')
    else:
        print('invalid choice of power units.')

digitize_and_save_plot(3, 'dBm')
