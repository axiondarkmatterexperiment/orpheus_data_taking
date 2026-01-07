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
from fitting_functions import data_lorentzian_fit, deconvolve_phase, calculate_coupling, func_pow_transmitted, func_pow_reflected

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


#logs either reflection or transmission scans in a separate table for displaying on grafana.
#Will log the fit as well. Assumes no fit data but if fit is provided it will log it.
def log_na_scan_for_display(scan_type, timestamp, freqs, pows, fit_pows=[]):
    #This function only exists for displaying the most recent NA scan on Grafana. It does not permanently save the trace. 
    ''' 
    Set up connection to the psql database
    '''

    # define the connection to the postgres database
    conn = psycopg2.connect(host='192.168.25.2', dbname='orpheus_db', user='postgres', password='axionsrock', port=5432)

    #I think this is just what we use to send commands directly to the postgres command line
    cur = conn.cursor()
    
    #format of data is {f:f_val0, p:power_val0, f:f_val1, p:power_val1, f:f_val2, p:power_val2, ...}
    #This is done so that Grafana can sort the array out into two columns and plot it in the x-y data form.
    if scan_type == "transmission" or scan_type == "trans":
        cur.execute("INSERT INTO transmission_display (timestamp, scan_type, freqs, pows) VALUES (%s,%s,%s,%s)",
                (timestamp, scan_type, freqs, pows))
        cur.execute("""CREATE TABLE IF NOT EXISTS public.transmission_display(
                    "timestamp" TIMESTAMPTZ,
                    freqs NUMERIC[],
                    pows NUMERIC[]
                    );
                    """)
        cur.execute("TRUNCATE TABLE transmission_display") #I only want this table to have a single NA scan in it at a time.
        cur.execute("INSERT INTO transmission_display (timestamp, freqs, pows) VALUES (%s,%s,%s)",
                (timestamp, freqs, pows))
        
        #I want to truncate the fit display table so old fits don't appear on new traces
        cur.execute("""CREATE TABLE IF NOT EXISTS public.transmission_fit_display(
                    "timestamp" TIMESTAMPTZ,
                    freqs NUMERIC[],
                    pows NUMERIC[]
                    );
                    """)
        cur.execute("TRUNCATE TABLE transmission_fit_display")
        cur.execute("INSERT INTO transmission_fit_display (timestamp, freqs, pows) VALUES (%s,%s,%s)",
                    (timestamp, freqs, fit_pows))

    elif scan_type == "reflection" or scan_type == "refl":
        cur.execute("""CREATE TABLE IF NOT EXISTS public.reflection_display(
                    "timestamp" TIMESTAMPTZ,
                    freqs NUMERIC[],
                    pows NUMERIC[]
                    );
                    """)
        cur.execute("TRUNCATE TABLE reflection_display") #I only want this table to have a single NA scan in it at a time.
        cur.execute("INSERT INTO reflection_display (timestamp, freqs, pows) VALUES (%s,%s,%s)",
                (timestamp, freqs, pows))
        
        #I want to truncate the fit display table so old fits don't appear on new traces
        cur.execute("""CREATE TABLE IF NOT EXISTS public.reflection_fit_display(
                    "timestamp" TIMESTAMPTZ,
                    freqs NUMERIC[],
                    pows NUMERIC[]
                    );
                    """)
        cur.execute("TRUNCATE TABLE reflection_fit_display")
        cur.execute("INSERT INTO reflection_fit_display (timestamp, freqs, pows) VALUES (%s,%s,%s)",
                    (timestamp, freqs, fit_pows))


    conn.commit()
    
    cur.close()
    conn.close()
    
    return

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
    re = iq[::2]
    im = iq[1::2]
    p = np.add(np.square(re),np.square(im)).astype(np.float64)
    p = p.tolist()
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
       
        p_fit = func_pow_transmitted(f, popt[0], popt[1], popt[2], popt[3])

        p = p.tolist()
        p_fit = p_fit.tolist()
        log_na_scan_for_display("transmission", timestamp, f, p, p_fit)
        return popt[0], popt[1]
    else:
        log_na_scan_for_display(fitting, "transmission", timestamp, f, p)
        return

def log_reflection_scan(f_center_GHz, f_span_GHz, na_power=-10, n_avgs=16, if_bw_Hz = 1e4, fitting=True):
    switch_rf("reflection")
    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
    f, iq = scan_na(f_center_GHz, f_span_GHz, na_power, n_avgs, if_bw_Hz) 
    re = iq[0::2]
    im = iq[1::2]
    p = np.add(np.square(re),np.square(im)).astype(np.float64)
    p = p.tolist()
    log_na_scan("reflection", timestamp, f, iq)
    if fitting:
        re, im = iq[::2], iq[1::2]
        p = np.square(re) + np.square(im)
        #try:
        popt, pcov = data_lorentzian_fit(p,f,'reflection')
        perr = np.sqrt(np.diag(pcov))
        log_cavity_params("f0_refl",timestamp, float(popt[0]))
        log_cavity_params("Q_refl",timestamp, float(popt[1]))
        log_cavity_params("dy_refl",timestamp, float(popt[2]))
        log_cavity_params("C_refl",timestamp, float(popt[3]))
         
        log_cavity_params("f0_err_refl",timestamp, float(perr[0]))
        log_cavity_params("Q_err_refl",timestamp, float(perr[1]))
        log_cavity_params("dy_err_refl",timestamp, float(perr[2]))
        log_cavity_params("C_err_refl",timestamp, float(perr[3]))
       
        phase = np.unwrap(np.angle(np.asarray(re)+1j*np.asarray(im)))
        cavity_phase = deconvolve_phase(f, phase)
        beta = calculate_coupling(popt[2]/popt[3],cavity_phase)
        
        log_cavity_params("beta",timestamp,float(beta))

        p_fit = func_pow_reflected(f, popt[0], popt[1], popt[2], popt[3]) 
        
        p = p.tolist()
        p_fit = p_fit.tolist()
        log_na_scan_for_display("reflection", timestamp, f, p, p_fit)

        return popt[0], popt[1], beta
    else:
        log_na_scan_for_display(fitting, "reflection", timestamp, f, p)
        return
