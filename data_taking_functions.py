#Log sensor values to the magnet_monitoring table
#assumes table is already made
import sys
import os

import numpy as np

sys.path.insert(0, 'magnet_supply_controller')
import psycopg2
import socket
import datetime
import pytz
#                                 side A temp, side B temp, hall 1, hall 2,  hall 3,   hall 4,  outside of can temp sensor
from calibration_functions import SN_U04844, SN_X201099, SN_68179, SN_68253, SN_64753, SN_67247, PT_100
from monitoring_functions import query_SCPI, write_SCPI
from fitting_functions import data_lorentzian_fit

def log_cavity_params(param_name, timestamp, val):
    ''' 
    Set up connection to the psql database
    '''

    # define the connection to the postgres database
    conn = psycopg2.connect(host='192.168.25.2', dbname='orpheus_db', user='postgres', password='axionsrock', port=5432)

    #I think this is just what we use to send commands directly to the postgres command line
    cur = conn.cursor()

    cur.execute("INSERT INTO cavity_params (param_name, timestamp, val) VALUES (%s, %s, %s)",
                (param_name, timestamp, val))
    
    conn.commit()
    
    cur.close()
    conn.close()

def log_na_scan(scan_type, timestamp, freqs, iq_data):
    ''' 
    Set up connection to the psql database
    '''

    # define the connection to the postgres database
    conn = psycopg2.connect(host='192.168.25.2', dbname='orpheus_db', user='postgres', password='axionsrock', port=5432)

    #I think this is just what we use to send commands directly to the postgres command line
    cur = conn.cursor()

    cur.execute("INSERT INTO na_scans (scan_type, timestamp, freqs, iq_data) VALUES (%s, %s, %s, %s)",
                (scan_type, timestamp, freqs, iq_data))
    
    conn.commit()
    
    cur.close()
    conn.close()

def switch_rf(setting): #setting values: "transmission", "reflection", "digitizer"
    IP_ADDRESS="192.168.25.9"
    PORT=1234
    TIMEOUT=3

    if setting == "transmission":
        ch1="0"
        ch2="0"
    elif setting == "reflection":
        ch1="0"
        ch2="1"
    elif setting == "digitization":
        ch1="1"
        ch2="0"
    else:
        print("not doing anything. make sure the setting is either transmission, reflection, or digitization.")
        return
   
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, "INST:SEL CH1\n")
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, "SOUR:OUTP:ENAB 1\n")
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, "SOUR:CHAN:OUTP:STAT " + ch1 + "\n")
    
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, "INST:SEL CH2\n")
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, "SOUR:OUTP:ENAB 1\n")
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT,"SOUR:CHAN:OUTP:STAT " + ch2 + "\n")

    return


def scan_na(f_center_GHz, f_span_GHz, na_power=-10, n_avgs=16, if_bw_Hz = 1e4):
    #send the query to the VNA:
    IP_ADDRESS="192.168.25.7"
    PORT=5025
    TIMEOUT=10 #This might need to be changed dependent on the averaging time

    #Sweep setup
    SCPI_string = "SENS1:FREQ:CENT " + str(f_center_GHz*1e9) + "\n"
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    SCPI_string = "SENS1:FREQ:SPAN " + str(f_span_GHz*1e9) + "\n"
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    SCPI_string = "SOUR:POW " + str(na_power) + "\n"
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)

    #Averaging
    SCPI_string = "SENS1:AVER:COUNT " + str(n_avgs) + "\n"
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    SCPI_string = "TRIG:AVER ON\n" #triggers the measurement
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    SCPI_string = "SENS1:BAND " + str(if_bw_Hz) + "\n" #triggers the measurement
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    
    #Triggering
    SCPI_string = "INIT1\n" #sets trigger to single
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    SCPI_string = "TRIG:SOUR BUS\n" #sets trigger source to bus
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    SCPI_string = "TRIG\n" #triggers the measurement
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    
    #Wait for measurement to finish
    SCPI_string = "*OPC?\n" #triggers the measurement
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    
    #Take scan data
    SCPI_string = "CALC1:DATA:SDAT?\n" #ask for the IQ data. Format: n*2-1 is real, n*2 is imaginary
    timestamp, iq_raw = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    SCPI_string = "SENS1:FREQ:DATA?\n" #ask for the frequency vector
    timestamp, f_raw = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)

    f_raw = np.fromstring(f_raw, dtype=np.float64, sep=',').tolist()
    iq_raw = np.fromstring(iq_raw, dtype=np.float64, sep=',').tolist()


    return f_raw, iq_raw 

def log_transmission_scan(f_center_GHz, f_span_GHz, na_power=-10, n_avgs=16, if_bw_Hz = 1e4, fitting=True):
    switch_rf("transmission")
    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
    f, iq = scan_na(f_center_GHz, f_span_GHz, na_power, n_avgs, if_bw_Hz) 
    log_na_scan("transmission", timestamp, f, iq)
    if fitting:
        re, im = iq[::2], iq[1::2]    
        p = np.square(re) + np.square(im)
        #try:
        popt, pcov = data_lorentzian_fit(p,f,'transmission')
        perr = np.sqrt(np.diag(pcov))
        log_cavity_params("f0_trans",timestamp, float(popt[0]))
        log_cavity_params("Q_trans",timestamp, float(popt[1]))
        log_cavity_params("dy_trans",timestamp, float(popt[2]))
        log_cavity_params("C_trans",timestamp, float(popt[3]))
         
        log_cavity_params("f0_err_trans",timestamp, float(perr[0]))
        log_cavity_params("Q_err_trans",timestamp, float(perr[1]))
        log_cavity_params("dy_err_trans",timestamp, float(perr[2]))
        log_cavity_params("C_err_trans",timestamp, float(perr[3]))
        
        return popt[0], popt[1]

def log_reflection_scan(f_center_GHz, f_span_GHz, na_power=-10, n_avgs=16, if_bw_Hz = 1e4, fitting=True):
    switch_rf("reflection")
    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
    f, iq = scan_na(f_center_GHz, f_span_GHz, na_power, n_avgs, if_bw_Hz) 
    log_na_scan("reflection", timestamp, f, iq)
    if fitting:
        re, im = iq[::2], iq[1::2]    
        p = np.square(re) + np.square(im)
        #try:
        popt, pcov = data_lorentzian_fit(p,f,'reflection')
        perr = np.sqrt(np.diag(pcov))
        log_cavity_params("f0_trans",timestamp, float(popt[0]))
        log_cavity_params("Q_trans",timestamp, float(popt[1]))
        log_cavity_params("dy_trans",timestamp, float(popt[2]))
        log_cavity_params("C_trans",timestamp, float(popt[3]))
         
        log_cavity_params("f0_err_trans",timestamp, float(perr[0]))
        log_cavity_params("Q_err_trans",timestamp, float(perr[1]))
        log_cavity_params("dy_err_trans",timestamp, float(perr[2]))
        log_cavity_params("C_err_trans",timestamp, float(perr[3]))
        
        return popt[0], popt[1]
