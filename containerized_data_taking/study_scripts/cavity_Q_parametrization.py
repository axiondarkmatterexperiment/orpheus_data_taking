from motor_functions import coordinated_motion, turn_cavity_around
from data_taking_functions import log_transmission_scan, log_reflection_scan
import numpy as np

'''
To run this script, set the cavity to its starting position. It will then run the cavity through the full range of motion
back and forth and record Q at repeated locations. This will give us a scatter of Q values for each cavity position, accounting
for the backlash.

I want to go from 13.5cm to 16.55cm in cavity lengths. I'd like to go back and forth about 5 times. 
'''

cavity_lengths_array = np.loadtxt('cavity_lengths_array.txt', dtype=np.float64, delimiter=',')
cavity_current_length = input("input the current cavity length: ")
cavity_current_length = float(cavity_current_length)

print(cavity_current_length)

