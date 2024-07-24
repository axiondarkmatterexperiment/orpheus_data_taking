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

#Hall sensor 1
#This is a hall effect magnetic field strength sensor, model HGCT-3020 from LakeShore
#The muxer reads out a voltage. These calibration values are assuming a 100 mA excitation current.
#The values_x are in Volts and the values_y are in kiloGauss
def SN_68179(voltage):
    # values_x = [-24.75739,-23.93484,-23.11216,-22.28932,-21.46634,-20.64321,-19.81993,-18.99651,-18.17295,-17.34923,-16.52538,-15.70139,-14.87725,-14.05296,-13.22854,-12.40399,-11.57926,-10.75431,-9.92915,-9.10377,-8.27804,-7.45186,-6.6253,-5.79832,-4.97093,-4.14316,-3.31502,-2.48652,-1.65777,-0.82897,-0.2487,-0.04145,0,0.04144,0.24866,0.82882,1.65765,2.48596,3.31392,4.14162,4.96892,5.79558,6.62184,7.4478,8.27331,9.09826,9.92278,10.74718,11.57142,12.39546,13.21935,14.04313,14.86683,15.69045,16.51398,17.33738,18.16066,18.98384,19.80691,20.62986,21.45271,22.27545,23.09808,23.9206,24.74302]
    values_x = [-0.02475739,-0.02393484,-0.02311216,-0.02228932,-0.02146634,-0.02064321,-0.01981993,-0.01899651,-0.01817295,-0.01734923,-0.01652538,-0.01570139,-0.01487725,-0.01405296,-0.01322854,-0.01240399,-0.01157926,-0.01075431,-0.00992915,-0.00910377,-0.00827804,-0.00745186,-0.0066253,-0.00579832,-0.00497093,-0.00414316,-0.00331502,-0.00248652,-0.00165777,-0.00082897,-0.0002487,-0.00004145,0,0.00004144,0.00024866,0.00082882,0.00165765,0.00248596,0.00331392,0.00414162,0.00496892,0.00579558,0.00662184,0.0074478,0.00827331,0.00909826,0.00992278,0.01074718,0.01157142,0.01239546,0.01321935,0.01404313,0.01486683,0.01569045,0.01651398,0.01733738,0.01816066,0.01898384,0.01980691,0.02062986,0.02145271,0.02227545,0.02309808,0.0239206,0.02474302]
    values_y = [-30,-29,-28,-27,-26,-25,-24,-23,-22,-21,-20,-19,-18,-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,-0.3,-0.05,0,0.05,0.3,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    return piecewise_cal(values_x,values_y,abs(voltage),log_x=False,log_y=False) #The relationship appears to be perfectly linear

#Hall sensor 2
#This is the hall effect magnetic field strength sensor, model HGCA-3020 from LakeShore
#The muxer reads out a voltage. These calibration values are assuming a 100 mA excitation current.
#The values_x are in Volts and the values_y are in kiloGauss
def SN_68253(voltage):
    values_x = [-0.02533235,-0.02450252,-0.02367162,-0.02283963,-0.02200657,-0.02117245,-0.02033726,-0.01950101,-0.01866371,-0.01782536,-0.01698597,-0.01614554,-0.01530407,-0.01446156,-0.01361804,-0.01277349,-0.01192973,-0.01108135,-0.01023376,-0.00938518,-0.00853555,-0.0076848,-0.00683338,-0.0059802,-0.00512614,-0.00427265,-0.00341867,-0.00256472,-0.00171049,-0.00085587,-0.00025757,-0.00004397,0,0.00004363,0.00025525,0.00085264,0.0017059,0.00255888,0.00341129,0.00426294,0.00511377,0.00596421,0.0068132,0.00766109,0.00850901,0.00935618,0.01020277,0.01104884,0.01189438,0.01273939,0.01358385,0.01442775,0.01527108,0.01611383,0.01695598,0.01779754,0.01863847,0.01947879,0.02031846,0.02115749,0.02199586,0.02283356,0.02367058,0.02450691,0.02534253]
    values_y = [-30,-29,-28,-27,-26,-25,-24,-23,-22,-21,-20,-19,-18,-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,-0.3,-0.05,0,0.05,0.3,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    return piecewise_cal(values_x,values_y,abs(voltage),log_x=False,log_y=False) #The relationship appears to be perfectly linear

#Hall sensor 3
#This is a hall effect magnetic field strength sensor, model HGCT-3020 from LakeShore
#The muxer reads out a voltage. These calibration values are assuming a 100 mA excitation current.
#The values_x are in Volts and the values_y are in kiloGauss
def SN_64753(voltage):
    values_x = [-0.02308314,-0.02232347,-0.02156303,-0.02080183,-0.02003988,-0.01927717,-0.01851372,-0.01774954,-0.01698462,-0.01621899,-0.01545264,-0.01468558,-0.0139178,-0.01314926,-0.01238,-0.01161022,-0.01083932,-0.01006689,-0.00929403,-0.00852195,-0.00774981,-0.00697658,-0.00620307,-0.00542924,-0.00465494,-0.00388023,-0.00310517,-0.00232974,-0.00155381,-0.00077722,-0.00023337,-0.00003884,0,0.00003882,0.0002327,0.00077654,0.00155297,0.00232947,0.00310581,0.00388174,0.00465728,0.00543261,0.0062076,0.00698202,0.00775618,0.00853011,0.00930386,0.01007773,0.01085094,0.01162278,0.01239408,0.01316489,0.01393497,0.01470437,0.01547311,0.0162412,0.01700865,0.01777543,0.01854155,0.01930698,0.02007173,0.02083578,0.02159912,0.02236175,0.02312364]
    values_y = [-30,-29,-28,-27,-26,-25,-24,-23,-22,-21,-20,-19,-18,-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,-0.3,-0.05,0,0.05,0.3,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    return piecewise_cal(values_x,values_y,abs(voltage),log_x=False,log_y=False) #The relationship appears to be perfectly linear

#Hall sensor 4
#This is a hall effect magnetic field strength sensor, model HGCT-3020 from LakeShore
#The muxer reads out a voltage. These calibration values are assuming a 100 mA excitation current.
#The values_x are in Volts and the values_y are in kiloGauss
def SN_67247(voltage):
    values_x = [-0.02568057,-0.02482847,-0.02397614,-0.02312357,-0.02227078,-0.02141777,-0.02056452,-0.01971105,-0.01885736,-0.01800343,-0.01714928,-0.01629493,-0.01544038,-0.01458566,-0.01373069,-0.01287542,-0.01201978,-0.01116374,-0.01030742,-0.00945095,-0.00859413,-0.0077368,-0.00687904,-0.0060208,-0.00516207,-0.00430295,-0.00344336,-0.00258328,-0.00172276,-0.00086163,-0.0002588,-0.00004308,0,0.00004303,0.00025796,0.00086102,0.00172292,0.00258482,0.00344657,0.00430822,0.00516975,0.00603107,0.0068921,0.00775284,0.00861326,0.00947323,0.0103329,0.01119248,0.01205178,0.01291064,0.01376907,0.01462713,0.01548497,0.01634272,0.0172003,0.01805767,0.01891483,0.01977176,0.02062848,0.02148498,0.02234125,0.02319731,0.02405315,0.02490877,0.02576416]
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
