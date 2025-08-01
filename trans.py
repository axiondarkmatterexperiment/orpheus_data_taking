from monitoring_functions import transmission_scan
center_f = float(input("input center frequency in GHz: "))
span_f = float(input("input frequency span in GHz: "))

freq, scan = transmission_scan(center_f, span_f)

import matplotlib
import matplotlib.pyplot as plt

import sys

import numpy as np

freq = np.fromstring(freq,dtype=float,sep=',')
scan = np.fromstring(scan,dtype=float,sep=',')
print(type(scan[0]))
re_scan = scan[1::2]
im_scan = scan[::2]
power = np.square(np.abs(re_scan))+np.square(np.abs(im_scan))

plt.plot(freq, power)
plt.savefig("scan_attempt.png")
