import math

'''

=============================   Functions related to calibrating raw sensor values       ==================================
||  The functions with names like "SN_X201099" take in a resistance measurement and spit out a temperature value based   ||
||  on a piecewise interpolation of the calibration file associated with the sensor's serial number, and the function    ||
||  name is the serial number of the sensor.                                                                             ||   
===========================================================================================================================

'''


#This is the magnet side B temperature sensor, a CX-1050-SD-HT Cernox sensor from LakeShore
#For these temperature sensors I am using log_x and log_y = True because the sensors appear
#to have a linear calibration on a log-log plot, implying a power law.
def SN_X201099(resistance):
    values_x = [75.0, 248.0, 2984.0]
    values_y = [295.0, 77.34, 4.2]
    return piecewise_cal(values_x,values_y, abs(resistance),log_x=True,log_y=True)

#This is the magnet side A temperature sensor, a RUOX-202A-AA-0.05B sensor from LakeShore
def SN_U04844(resistance):
    values_x = [2200,2210,2230,2240,2260,2270,2280,2290,2300,2320,2330,2350,2360,2370,2380,2390,2410,2420,2440,2460,2480,2500,2530,2560,2600,2650,2700,2740,2780,2820,2880,2900,2930,2960,2990,3030,3070,3110,3160,3220,3290,3370,3470,3590,3740,3830,3940,4010,4130,4290,4480,4700,4930,5230,5590,5970,6450,6990,7520,7850,8240,8920,9800,10800,11900,13200,14600,16800,19500,23400,27700,32700,40200,48200,55400,61800,72700]
    values_y = [45,42,39,36,33,30.9,29.1,27.5,25.9,24.3,22.7,21.2,20.1,19.1,18.2,17.2,16.3,15.3,14.4,13.4,12.4,11.4,10.3,9.27,8.22,7.17,6.33,5.61,5.09,4.68,4.2,4,3.8,3.6,3.4,3.2,3,2.8,2.6,2.4,2.2,2,1.8,1.6,1.4,1.3,1.2,1.14,1.05,0.95,0.856,0.767,0.688,0.611,0.536,0.476,0.417,0.367,0.328,0.309,0.289,0.26,0.23,0.205,0.184,0.164,0.149,0.13,0.113,0.0965,0.0844,0.0752,0.0653,0.0572,0.0518,0.0481,0.0439]
    return piecewise_cal(values_x,values_y,abs(resistance),log_x=True,log_y=True)

#This is the can_outside_bottom_temp sensor
#I can't find the serial number of this one
def PT_100(resistance):
    values_x = [1.14,2.29,9.39,18.52,39.72,60.26,80.31,100,119.4,138.51]
    values_y = [4.2,20,50,73.15,123.15,173.15,223.15,273.15,323.15,373.15]
    return piecewise_cal(values_x,values_y,abs(resistance),log_x=True,log_y=True)

#This is the hall effect magnetic field strength sensor, model HGCT-3020 from LakeShore
#The muxer reads out a voltage. These calibration values are assuming a 100 mA excitation current.
#The values_x are in Volts and the values_y are in kiloGauss
def SN_68179(voltage):
    # values_x = [-24.75739,-23.93484,-23.11216,-22.28932,-21.46634,-20.64321,-19.81993,-18.99651,-18.17295,-17.34923,-16.52538,-15.70139,-14.87725,-14.05296,-13.22854,-12.40399,-11.57926,-10.75431,-9.92915,-9.10377,-8.27804,-7.45186,-6.6253,-5.79832,-4.97093,-4.14316,-3.31502,-2.48652,-1.65777,-0.82897,-0.2487,-0.04145,0,0.04144,0.24866,0.82882,1.65765,2.48596,3.31392,4.14162,4.96892,5.79558,6.62184,7.4478,8.27331,9.09826,9.92278,10.74718,11.57142,12.39546,13.21935,14.04313,14.86683,15.69045,16.51398,17.33738,18.16066,18.98384,19.80691,20.62986,21.45271,22.27545,23.09808,23.9206,24.74302]
    values_x = [-0.02475739,-0.02393484,-0.02311216,-0.02228932,-0.02146634,-0.02064321,-0.01981993,-0.01899651,-0.01817295,-0.01734923,-0.01652538,-0.01570139,-0.01487725,-0.01405296,-0.01322854,-0.01240399,-0.01157926,-0.01075431,-0.00992915,-0.00910377,-0.00827804,-0.00745186,-0.0066253,-0.00579832,-0.00497093,-0.00414316,-0.00331502,-0.00248652,-0.00165777,-0.00082897,-0.0002487,-0.00004145,0,0.00004144,0.00024866,0.00082882,0.00165765,0.00248596,0.00331392,0.00414162,0.00496892,0.00579558,0.00662184,0.0074478,0.00827331,0.00909826,0.00992278,0.01074718,0.01157142,0.01239546,0.01321935,0.01404313,0.01486683,0.01569045,0.01651398,0.01733738,0.01816066,0.01898384,0.01980691,0.02062986,0.02145271,0.02227545,0.02309808,0.0239206,0.02474302]
    values_y = [-30,-29,-28,-27,-26,-25,-24,-23,-22,-21,-20,-19,-18,-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,-0.3,-0.05,0,0.05,0.3,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    return piecewise_cal(values_x,values_y,abs(voltage),log_x=False,log_y=False) #The relationship appears to be perfectly linear

#This function was mostly copied from https://github.com/axiondarkmatterexperiment/dragonfly-extended/blob/master/source/admx_muxer_cals.py
# but I removed the lines that use dripline to log warnings.
def piecewise_cal(values_x, values_y, this_x, log_x=False, log_y=False):
    if log_x:
        values_x = [math.log(x) for x in values_x]
        this_x = math.log(this_x)
    if log_y:
        values_y = [math.log(y) for y in values_y]
    try:
        high_index = [i>this_x for i in values_x].index(True)
    except ValueError:
        high_index = -1
    if high_index == 0:
        high_index = 1
    m = (values_y[high_index] - values_y[high_index - 1]) / (values_x[high_index] - values_x[high_index - 1])
    to_return = values_y[high_index - 1] + m * (this_x - values_x[high_index - 1])
    if log_y:
        to_return = math.exp(to_return)
    return to_return
