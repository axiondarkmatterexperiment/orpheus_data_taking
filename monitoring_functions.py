#Log sensor values to the magnet_monitoring table
#assumes table is already made
import sys
import os

sys.path.insert(0, 'magnet_supply_controller')
import psycopg2
import socket
import datetime
import pytz
#                                 side A temp, side B temp, hall 1, hall 2,  hall 3,   hall 4,  outside of can temp sensor
from calibration_functions import SN_U04844, SN_X201099, SN_68179, SN_68253, SN_64753, SN_67247, PT_100

def monitor_experiment():
    log_magnet_temps()
    log_outside_can_temp()
    log_hall_sensors()
    log_resistor_dewar_bottom()
    #log_LHe_level()
    #Add other parts as other parts become functional. Currently thinking of:
    #  1) magnet supply current
    #  2) log outside can bottom temperature

def establish_databases():
    ''' 
    Set up connection to the psql database
    '''

    # define the connection to the postgres database
    # conn = psycopg2.connect(host='192.168.25.2', dbname='postgres', user='admx_master', password='wimpssuck', port=5432)
    conn = psycopg2.connect(host='192.168.25.2', dbname='orpheus_db', user='postgres', password='axionsrock', port=5432)

    #I think this is just what we use to send commands directly to the postgres command line
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS public.experiment_log (
                "timestamp" TIMESTAMPTZ,
                type TEXT,
                task TEXT,
                message TEXT
                );
                """)
    
    cur.execute("""CREATE TABLE IF NOT EXISTS public.magnet_monitoring (
                sensor_name TEXT,
                "timestamp" TIMESTAMPTZ,
                val_raw REAL,
                val_cal REAL
                );
                """)
    
    cur.execute("DROP TABLE IF EXISTS current_task;")

    cur.execute("""CREATE TABLE public.current_task (
                "timestamp" TIMESTAMPTZ,
                task TEXT
                );
                """)
    
    #I insert values into current_task so that they can be replaced by UPDATE in the update_current_task function.
    # If the table does not have a populated row then updating it will do nothing.
    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
    task = 'establishing databases'
    cur.execute("INSERT INTO current_task(timestamp, task) VALUES (%s, %s)", (timestamp, task))
    
    conn.commit()
    
    cur.close()
    conn.close()

def update_current_task(current_task):
    ''' 
    Set up connection to the psql database
    '''

    # define the connection to the postgres database
    # conn = psycopg2.connect(host='192.168.25.2', dbname='postgres', user='admx_master', password='wimpssuck', port=5432)
    conn = psycopg2.connect(host='192.168.25.2', dbname='orpheus_db', user='postgres', password='axionsrock', port=5432)

    #I think this is just what we use to send commands directly to the postgres command line
    cur = conn.cursor()
    
    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))
    task = 'establishing databases'
    cur.execute("UPDATE current_task SET timestamp = %s, task = %s", (timestamp, current_task))
    
    conn.commit()
    
    cur.close()
    conn.close()


def log_error(timestamp, error_message):
    ''' 
    Set up connection to the psql database
    '''

    # define the connection to the postgres database
    # conn = psycopg2.connect(host='192.168.25.2', dbname='postgres', user='admx_master', password='wimpssuck', port=5432)
    conn = psycopg2.connect(host='192.168.25.2', dbname='orpheus_db', user='postgres', password='axionsrock', port=5432)

    #I think this is just what we use to send commands directly to the postgres command line
    cur = conn.cursor()

    cur.execute("SELECT task FROM current_task;")

    #I am indexing [3:-4] because the output of this is formatted as: [('contents_of_task_string',)] and I only want contents_of_task_string .... this is for purely aesthetic purposes
    task = str(cur.fetchall())[3:-4]
    type = "error"

    cur.execute("INSERT INTO experiment_log (timestamp, type, task, message) VALUES (%s, %s, %s, %s)",
                (timestamp, type, task, error_message))
    
    conn.commit()
    
    cur.close()
    conn.close()

def log_sensor(sensor_name, timestamp, val_raw, val_cal ):
    ''' 
    Set up connection to the psql database
    '''

    # define the connection to the postgres database
    # conn = psycopg2.connect(host='192.168.25.2', dbname='postgres', user='admx_master', password='wimpssuck', port=5432)
    conn = psycopg2.connect(host='192.168.25.2', dbname='orpheus_db', user='postgres', password='axionsrock', port=5432)

    #I think this is just what we use to send commands directly to the postgres command line
    cur = conn.cursor()

    cur.execute("INSERT INTO magnet_monitoring (sensor_name, timestamp, val_raw, val_cal) VALUES (%s, %s, %s, %s)",
                (sensor_name, timestamp, val_raw, val_cal))
    
    conn.commit()
    
    cur.close()
    conn.close()

def log_magnet_temps():
    update_current_task('logging magnet temperatures')
    #Send the query to the LHe level sensor
    IP_ADDRESS="192.168.25.11"
    PORT=1234 #The one that Raphael used. I tried a few other values and got the error that "the target machine actively refused" the connection
    TIMEOUT=5 #This was the value Raphael used
    MEAS_SIDE_A = "MEAS:FRES? (@107)\n" #Should I specify the resolution and whatever? Check documentation
    MEAS_SIDE_B = "MEAS:FRES? (@108)\n" #Should I specify the resolution and whatever? Check documentation

    timestamp_side_A, val_raw_side_A = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, MEAS_SIDE_A)
    timestamp_side_B, val_raw_side_B = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, MEAS_SIDE_B)

    val_raw_side_A = float(val_raw_side_A)
    val_raw_side_B = float(val_raw_side_B)

    #Log the magnet side A temperature sensor value
    sensor_name_side_A = "magnet_side_A_temp"
    sensor_name_side_B = "magnet_side_B_temp"

    val_cal_side_A = SN_U04844(val_raw_side_A)
    val_cal_side_B = SN_X201099(val_raw_side_B)

    log_sensor(sensor_name_side_A, timestamp_side_A, val_raw_side_A, val_cal_side_A)
    log_sensor(sensor_name_side_B, timestamp_side_B, val_raw_side_B, val_cal_side_B)

def log_outside_can_temp():
    update_current_task('logging magnet temperatures')
    #Send the query to the LHe level sensor
    IP_ADDRESS="192.168.25.11"
    PORT=1234 #The one that Raphael used. I tried a few other values and got the error that "the target machine actively refused" the connection
    TIMEOUT=5 #This was the value Raphael used
    MEAS_OUTSIDE_CAN = "MEAS:FRES? (@106)\n" #Should I specify the resolution and whatever? Check documentation

    timestamp_outside_can, val_raw_outside_can = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, MEAS_OUTSIDE_CAN)

    val_raw_outside_can = float(val_raw_outside_can)

    #Log the magnet side A temperature sensor value
    sensor_name_outside_can = "outside_can_temp"

    val_cal_outside_can = PT_100(val_raw_outside_can)

    log_sensor(sensor_name_outside_can, timestamp_outside_can, val_raw_outside_can, val_cal_outside_can)



def log_resistor_dewar_bottom():
    update_current_task('logging magnet resistor at the bottom of the dewar')
    #Send the query to the LHe level sensor
    IP_ADDRESS="192.168.25.11"
    PORT=1234 #The one that Raphael used. I tried a few other values and got the error that "the target machine actively refused" the connection
    TIMEOUT=5 #This was the value Raphael used
    MEAS_DEWAR_RESISTOR = "MEAS:RES? (@109)\n" #Should I specify the resolution and whatever? Check documentation

    timestamp_dewar_resistor, val_raw_dewar_resistor = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, MEAS_DEWAR_RESISTOR)

    val_raw_dewar_resistor = float(val_raw_dewar_resistor)

    #Log the magnet side A temperature sensor value
    sensor_name_dewar_resistor = "dewar_bottom_resistor_resistance"

    val_cal_dewar_resistor = val_raw_dewar_resistor

    log_sensor(sensor_name_dewar_resistor, timestamp_dewar_resistor, val_raw_dewar_resistor, val_cal_dewar_resistor)

#This function accounts for whether the output is on or off. if the output is off then the applied current is zero, and this records it as such.
def log_hall_sensors():
    update_current_task('logging hall sensor')
    #Send the query to the hall effect sensor's voltage readout
    IP_ADDRESS="192.168.25.11"
    PORT=1234 #The one that Raphael used. I tried a few other values and got the error that "the target machine actively refused" the connection
    TIMEOUT=5 #This was the value Raphael used
    
    #Hall sensor 1
    HALL_SENSOR_SCPI = "MEAS:VOLT? (@101)\n" #Should I specify the resolution and whatever? Check documentation
    timestamp_hall_sensor, val_raw_hall_sensor = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, HALL_SENSOR_SCPI)
    val_raw_hall_sensor = float(val_raw_hall_sensor)
    sensor_name_hall_sensor = "hall_sensor_1"
    val_cal_hall_sensor = SN_68179(val_raw_hall_sensor) #nonsense placeholder for right now. Will drop the table before putting in real values.
    log_sensor(sensor_name_hall_sensor, timestamp_hall_sensor, val_raw_hall_sensor, val_cal_hall_sensor)

    #Hall sensor 2
    HALL_SENSOR_SCPI = "MEAS:VOLT? (@102)\n" #Should I specify the resolution and whatever? Check documentation
    timestamp_hall_sensor, val_raw_hall_sensor = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, HALL_SENSOR_SCPI)
    val_raw_hall_sensor = float(val_raw_hall_sensor)
    sensor_name_hall_sensor = "hall_sensor_2"
    val_cal_hall_sensor = SN_68253(val_raw_hall_sensor) #nonsense placeholder for right now. Will drop the table before putting in real values.
    log_sensor(sensor_name_hall_sensor, timestamp_hall_sensor, val_raw_hall_sensor, val_cal_hall_sensor)

    #Hall sensor 3
    HALL_SENSOR_SCPI = "MEAS:VOLT? (@103)\n" #Should I specify the resolution and whatever? Check documentation
    timestamp_hall_sensor, val_raw_hall_sensor = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, HALL_SENSOR_SCPI)
    val_raw_hall_sensor = float(val_raw_hall_sensor)
    sensor_name_hall_sensor = "hall_sensor_3"
    val_cal_hall_sensor = SN_64753(val_raw_hall_sensor) #nonsense placeholder for right now. Will drop the table before putting in real values.
    log_sensor(sensor_name_hall_sensor, timestamp_hall_sensor, val_raw_hall_sensor, val_cal_hall_sensor)
   
    #Hall sensor 4
    HALL_SENSOR_SCPI = "MEAS:VOLT? (@104)\n" #Should I specify the resolution and whatever? Check documentation
    timestamp_hall_sensor, val_raw_hall_sensor = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, HALL_SENSOR_SCPI)
    val_raw_hall_sensor = float(val_raw_hall_sensor)
    sensor_name_hall_sensor = "hall_sensor_4"
    val_cal_hall_sensor = SN_67247(val_raw_hall_sensor) #nonsense placeholder for right now. Will drop the table before putting in real values.
    log_sensor(sensor_name_hall_sensor, timestamp_hall_sensor, val_raw_hall_sensor, val_cal_hall_sensor)

    #Check the excitation current -- this is technically not a measurement, but just to document that it is at 100 mA, as we want it to be
    #Send query to the Yokogawa GS200 current source
    IP_ADDRESS="192.168.25.14"
    PORT=7655 #The one that Raphael used. I tried a few other values and got the error that "the target machine actively refused" the connection
    TIMEOUT=5 #This was the value Raphael used
    HALL_CURRENT_SCPI = "SOUR:LEV?\n" #Should I specify the resolution and whatever? Check documentation

    timestamp_hall_current, val_raw_hall_current = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, HALL_CURRENT_SCPI)

    OUTPUT_SCPI = "OUTP?\n"
    timestamp_throwaway, output_str = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, OUTPUT_SCPI)

    val_raw_hall_current = float(output_str)*float(val_raw_hall_current)

    #Log the magnet side A temperature sensor value
    sensor_name_hall_current = "hall_sensor_applied_current"

    val_cal_hall_current = val_raw_hall_current #I believe no calibration needs to be done for this. So this is redundant but keeping it for consistency

    log_sensor(sensor_name_hall_current, timestamp_hall_current, val_raw_hall_current, val_cal_hall_current)

#Current in amps is input as a floating point, output_setting as a string (either "ON" or "OFF")
def set_hall_excitation_current(current_in_amps, output_setting): #This does not allow you to set the current above 0.1 Amps
    update_current_task('setting hall sensor excitation current')
    IP_ADDRESS="192.168.25.14"
    PORT=7655 #the manual mentions this one on page 11-5 "You can set the terminator that is used to send data from the command control server at port 7655"
    TIMEOUT=5 #tested and works so far

    SCPI_string = "*IDN?\n" #Check connection
    print(query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)[1])
    

    # SCPI_string = "SOUR:FUNC CURR;RANG 0.1?\n" #Set the current range to max out at the desired current (running too much current might damage the sensor)
    # query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    
    SCPI_string = "SOUR:FUNC CURR\n" #Set the current range to max out at the desired current (running too much current might damage the sensor)
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
    
    SCPI_string = "SOUR:RANG 0.1\n" #Set the current range to max out at the desired current (running too much current might damage the sensor)
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)

    SCPI_string = "SOUR:LEV " + str(current_in_amps) + "\n" #Set the current level to 0.1 Amps (100 mA)
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)

    SCPI_string = "OUTP:STAT " + output_setting + "\n"
    write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)

    output_type_voltage_or_current = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "SOUR:FUNC?\n")[1]
    output_in_volts_or_amps = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "SOUR:LEV?\n")[1]
    
    return output_type_voltage_or_current, output_in_volts_or_amps

#This function assumes that the LHe level sensor box is already in CONTINUOUS mode for measurements
# this is because it is blocking write commands, and we can only request info from it. I'm not sure why.
# so we need to have the level sensor continually read the level, then we can query for it's last measurement with MEAS?
# It also assumes that the sensor is reading in inches.
# Then the val_raw is in inches, and the val_cal is in percentage of the sensor length
def log_LHe_level():
    update_current_task('logging LHe level')
    #Send the query to the LHe level sensor
    IP_ADDRESS="192.168.25.13"
    PORT=4266 #The one that Raphael used. I tried a few other values and got the error that "the target machine actively refused" the connection
    TIMEOUT=3 #This was the value Raphael used
    #SCPI_string = "*OPC?\n" #Check connection
    #print(query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string))

    
    SCPI_string = "MEAS?\n"
    
    sensor_length_cm = 120
    sensor_length_inches = 120/2.54

    timestamp, val_raw = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)

    #Log the magnet side A temperature sensor value
    sensor_name = "LHe_level"

    val_cal = 100*val_raw/sensor_length_inches #assuming that the sensor is set to read out in inches

    log_sensor(sensor_name, timestamp, val_raw, val_cal)

#Switches for the RF path are controlled by the Keithley power supply.
#The power supply has two channels. The switch settings are:
#   TRANSMISSION: CH1=OFF, CH2=OFF
#   REFLECTION: CH1=ON, CH2=OFF
#   DIGITIZATION: CH1=OFF, CH2=ON
def switch_rf(setting): #setting values: "transmission", "reflection", "digitizer"
    IP_ADDRESS="192.158.25.9"
    PORT="1234"
    TIMEOUT=3

    if setting == "transmission":
        SCPI_string = "INST:SEL CH1\n"
        write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
        query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "*OPC?\n")
        SCPI_string = "SOUR:OUTP:ENAB 0"
        write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
        query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "*OPC?\n")
        
        SCPI_string = "INST:SEL CH2\n"
        write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
        query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "*OPC?\n")
        SCPI_string = "SOUR:OUTP:ENAB 0"
        write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)
        query_SCPI(IP_ADDRESS, PORT, TIMEOUT, "*OPC?\n")



def scan_na(f_center_GHz, f_span_GHz, na_power=-10, n_avgs=16, if_bw_Hz = 1e4):
    update_current_task('transmission scan')
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

    

    return f_raw, iq_raw 

def query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string):
    # update_current_task('sending SCPI Query:',SCPI_string) #This might just be annoying
    #Establish connection via the socket
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_connection.settimeout(TIMEOUT)
    socket_connection.connect((IP_ADDRESS, PORT))

    # Send encoded message and record time of the measurement
    socket_connection.sendall(SCPI_string.encode())
    timestamp = datetime.datetime.now(pytz.timezone('US/Pacific'))

    # Apply recv until a message with a newline at the end is received
    recv_bytes = bytes(0)  # Empty bytes
    while True:
        recv_bytes += socket_connection.recv(4096)
        # print(recv_bytes.decode())
        if recv_bytes[-1:] == b"\n":  # Check if last term is a newline
            break

    val_raw = recv_bytes.decode()

    return timestamp, val_raw
    

#This is for sending SCPI commands which you don't expect any response for. (Using query_SCPI for said commands causes a timeout error).
#NOTE: that this only TRIES to write your command. It doesn't check if it actually worked. To check if it worked you can use query_SCPI.
def write_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string):
    
    # update_current_task('sending SCPI Query:',SCPI_string) #This might just be annoying
    #Establish connection via the socket
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_connection.settimeout(TIMEOUT)
    socket_connection.connect((IP_ADDRESS, PORT))

    # Send encoded message and record time of the measurement
    socket_connection.sendall(SCPI_string.encode())
    return

