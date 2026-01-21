#Log sensor values to the magnet_monitoring table
#assumes table is already made
import sys
import os
import time

import numpy as np
import io

sys.path.insert(0, 'magnet_supply_controller')
import psycopg2
import socket
import datetime
import pytz
#                                 side A temp, side B temp, hall 1, hall 2,  hall 3,   hall 4,  outside of can temp sensor
from calibration_functions import SN_U04844, SN_X201099, SN_68179, SN_68253, SN_64753, SN_67247, PT_100
from monitoring_functions import query_SCPI, write_SCPI, log_error
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

def log_digitization(timestamp, freqs, pows):
    ''' 
    Set up connection to the psql database
    '''

    # define the connection to the postgres database
    conn = psycopg2.connect(host='192.168.25.2', dbname='orpheus_db', user='postgres', password='axionsrock', port=5432)

    #I think this is just what we use to send commands directly to the postgres command line
    cur = conn.cursor()

    cur.execute("INSERT INTO digitizations (timestamp, freqs, pows) VALUES (%s, %s, %s)",
                (timestamp, freqs, pows))
    
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
    elif setting == "digitizer":
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
    TIMEOUT=5 #This might need to be changed dependent on the averaging time

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

    if f_raw and iq_raw:
        f_raw = np.fromstring(f_raw, dtype=np.float64, sep=',').tolist()
        iq_raw = np.fromstring(iq_raw, dtype=np.float64, sep=',').tolist()
    #If the query_SCPI times out then it returns False for the val_raw, in which case I want an empty list.
    else:
        iq_raw = []
        f_raw = []

    return f_raw, iq_raw 

def log_transmission_scan(f_center_GHz, f_span_GHz, na_power=-10, n_avgs=16, if_bw_Hz = 1e4, fitting=True, param_logging=True):
    switch_rf("transmission")
    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
    f, iq = scan_na(f_center_GHz, f_span_GHz, na_power, n_avgs, if_bw_Hz) 
    if f and iq:
        re = iq[::2]
        im = iq[1::2]
        p = np.add(np.square(re),np.square(im)).astype(np.float64)
        p = p.tolist()
        log_na_scan("transmission", timestamp, f, iq)
        if fitting:
            re, im = iq[::2], iq[1::2]    
            p = np.square(re) + np.square(im)
            try:
                popt, pcov = data_lorentzian_fit(p,f,'transmission')
                perr = np.sqrt(np.diag(pcov))
                p_fit = func_pow_transmitted(f, popt[0], popt[1], popt[2], popt[3])
                p_fit = p_fit.tolist()
            except:
                popt = [np.nan, np.nan, np.nan, np.nan]
                perr = [np.nan, np.nan, np.nan, np.nan]
                p_fit = []
                print("fit failed")
            if param_logging==True:
                log_cavity_params("f0_trans",timestamp, float(popt[0]))
                log_cavity_params("Q_trans",timestamp, float(popt[1]))
                log_cavity_params("dy_trans",timestamp, float(popt[2]))
                log_cavity_params("C_trans",timestamp, float(popt[3]))
                 
                log_cavity_params("f0_err_trans",timestamp, float(perr[0]))
                log_cavity_params("Q_err_trans",timestamp, float(perr[1]))
                log_cavity_params("dy_err_trans",timestamp, float(perr[2]))
                log_cavity_params("C_err_trans",timestamp, float(perr[3]))

            p = p.tolist()
            log_na_scan_for_display("transmission", timestamp, f, p, p_fit)
            return popt[0], popt[1]
        else:
            log_na_scan_for_display(fitting, "transmission", timestamp, f, p)
            return
    else:
        log_error(timestamp, "empty trans, SCPI timeout likely")
        return


def log_reflection_scan(f_center_GHz, f_span_GHz, na_power=-10, n_avgs=16, if_bw_Hz = 1e4, fitting=True, param_logging=True):
    switch_rf("reflection")
    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
    f, iq = scan_na(f_center_GHz, f_span_GHz, na_power, n_avgs, if_bw_Hz) 
    if f and iq:
        re = iq[0::2]
        im = iq[1::2]
        p = np.add(np.square(re),np.square(im)).astype(np.float64)
        p = p.tolist()
        log_na_scan("reflection", timestamp, f, iq)
        if fitting:
            re, im = iq[::2], iq[1::2]
            p = np.square(re) + np.square(im)
            try:
                popt, pcov = data_lorentzian_fit(p,f,'reflection')
                perr = np.sqrt(np.diag(pcov))
                p_fit = func_pow_reflected(f, popt[0], popt[1], popt[2], popt[3])
                p_fit = p_fit.tolist()
            except:
                popt = [np.nan, np.nan, np.nan, np.nan]
                perr = [np.nan, np.nan, np.nan, np.nan]
                p_fit = []
                print("fit failed")
            if param_logging==True:
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

            p = p.tolist()
            log_na_scan_for_display("reflection", timestamp, f, p, p_fit)

            return popt[0], popt[1], beta
        else:
            log_na_scan_for_display(fitting, "reflection", timestamp, f, p)
            return
    else:
        log_error(timestamp, "empty refl, SCPI timeout likely")
        return
    
def log_transmission_widescan(f_center_GHz, f_span_GHz, na_power=-5, n_avgs=30, if_bw_Hz = 1e4):
    switch_rf("transmission")
    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
    f, iq = scan_na(f_center_GHz, f_span_GHz, na_power, n_avgs, if_bw_Hz)
    re = iq[0::2]
    im = iq[1::2]
    p = np.add(np.square(re),np.square(im)).astype(np.float64)
    p = p.tolist()
    log_na_scan("transmission_widescan", timestamp, f, p)
    return f, p

def set_lo_center_freq(center_freq):
    IP_ADDRESS = "192.168.25.10"
    PORT = 5025
    TIMEOUT = 5
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, "FREQ:CW " + str(center_freq) + "\n")
    #Check that it has been set properly, return false / zero if not:
    timestamp, f_set = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "FREQ:CW?\n")
    if float(f_set) == center_freq:
        return f_set
    else:
        return 0

def digitize(acquisition_time):
    switch_rf("digitizer")
    IP_ADDRESS = "192.168.25.8"
    PORT = 50000
    TIMEOUT=5
    set_acq_time_string = "SET:ACQUISITION_TIME " + str(acquisition_time) + "\n"
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, set_acq_time_string)
    time.sleep(0.01)
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, "START\n")
    wait_for_digitization()
    timestamp, spectrum = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "GET:LAST_SPECTRUM?\n")
    spectrum = io.StringIO(spectrum)
    spectrum = np.genfromtxt(spectrum,dtype=float,delimiter=None)
    #spectrum = spectrum.T
    pows = spectrum.tolist()
    freqs = np.arange(np.size(pows)).tolist()
    log_digitization(timestamp, freqs, pows)
    return timestamp, spectrum
    
def wait_for_digitization():
    IP_ADDRESS = "192.168.25.8"
    PORT = 50000
    TIMEOUT=5

    digitizing = True
    while digitizing:
        timestamp, dig_status = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "GET:STATUS?\n")
        dig_status = dig_status[0:-1] #Remove the \n on the end of the returned string
        print(dig_status)
        if dig_status == "RUNNING":
            digitizing = True
        elif dig_status == "IDLE":
            digitizing = False
        time.sleep(1)
    return

def tune_while_tracking_mode(initial_f0_GHz, initial_span_GHz, tune_distance_cm, tune_increment_cm, measure_coupling=True):
    from motor_functions import coordinated_motion
    na_span_GHz = initial_span_GHz
    na_fc_GHz = initial_f0_GHz
    num_steps = int(tune_distance_cm/tune_increment_cm)
    min_Q = 1000 #If measured Q is below this then ignore it and use this value
    max_Q = 6000 #If measured Q is above this then ignore it and use this value
    j=0
    while j<num_steps:
        #Look at a wider window after tuning to find the f0 and rough estimate of QL. Don't log the measured cavity parameters
        na_span_GHz=2*na_span_GHz
        na_fc, current_QL = log_transmission_scan(na_fc_GHz, na_span_GHz, param_logging=False)
        time.sleep(0.1)
        na_fc_GHz = na_fc/1e9
        #Make the window smaller around the approximate peak and retake the transmission scan. Log the measured cavity parameters
        na_span_GHz = na_span_GHz/2
        na_fc, current_QL = log_transmission_scan(na_fc_GHz, na_span_GHz, param_logging=False)
        time.sleep(0.1)
        na_fc_GHz = na_fc/1e9
        if current_QL > min_Q and current_QL < max_Q:
            na_span_GHz = 5*na_fc_GHz/current_QL
        elif current_QL < min_Q:
            na_span_GHz = 5*na_fc_GHz/min_Q
        else:
            na_span_GHz = 5*na_fc_GHz/max_Q
        na_fc, current_QL = log_transmission_scan(na_fc_GHz, na_span_GHz, param_logging=True)
        time.sleep(0.1)
        if measure_coupling:
            log_reflection_scan(na_fc_GHz, na_span_GHz/1.7, param_logging=True)
        #Only keep tuning if we have a good fit
        if np.isnan(current_QL)==False:
            coordinated_motion(tune_increment_cm)
            time.sleep(0.1)
            j=j+1
    return j*tune_increment_cm


