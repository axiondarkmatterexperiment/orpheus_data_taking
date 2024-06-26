#Log sensor values to the magnet_monitoring table
#assumes table is already made

import psycopg2
import socket
import datetime

def log_sensor(sensor_name, timestamp, val_raw, val_cal ):
    ''' 
    Set up connections to the psql database, VNA, and motor
    '''

    # define the connection to the postgres database
    conn = psycopg2.connect(host='192.168.25.2', dbname='postgres', user='admx_master', password='wimpssuck', port=5432)

    #I think this is just what we use to send commands directly to the postgres command line
    cur = conn.cursor()

    cur.execute("INSERT INTO magnet_monitoring (sensor_name, timestamp, val_raw, val_cal) VALUES (%s, %s, %s, %s)",
                (sensor_name, timestamp, val_raw, val_cal))
    
    conn.commit()
    
    cur.close()
    conn.close()

def log_magnet_temps():
    #Send the query to the LHe level sensor
    IP_ADDRESS="192.168.25.11"
    PORT=1234 #The one that Raphael used. I tried a few other values and got the error that "the target machine actively refused" the connection
    TIMEOUT=5 #This was the value Raphael used
    MEAS_SIDE_A = "MEAS:FRES? (@108)\n" #Should I specify the resolution and whatever? Check documentation
    MEAS_SIDE_B = "MEAS:FRES? (@109)\n" #Should I specify the resolution and whatever? Check documentation

    timestamp_side_A, val_raw_side_A = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, MEAS_SIDE_A)
    timestamp_side_B, val_raw_side_B = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, MEAS_SIDE_B)

    val_raw_side_A = float(val_raw_side_A)
    val_raw_side_B = float(val_raw_side_B)

    #Log the magnet side A temperature sensor value
    sensor_name_side_A = "LHe_level"
    sensor_name_side_B = "LHe_level"

    val_cal_side_A = val_raw_side_A*2 #nonsense placeholder for right now. Will drop the table before putting in real values.
    val_cal_side_B = val_raw_side_B*2

    log_sensor(sensor_name_side_A, timestamp_side_A, val_raw_side_A, val_cal_side_A)
    log_sensor(sensor_name_side_B, timestamp_side_B, val_raw_side_B, val_cal_side_B)


def log_LHe_level():
    #Send the query to the LHe level sensor
    IP_ADDRESS="192.168.25.13"
    PORT=4266 #The one that Raphael used. I tried a few other values and got the error that "the target machine actively refused" the connection
    TIMEOUT=5 #This was the value Raphael used
    SCPI_string = "******\n" #I need to figure out what to put here

    timestamp, val_raw = query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string)

    #Log the magnet side A temperature sensor value
    sensor_name = "LHe_level"


    val_cal = val_raw*2 #nonsense placeholder for right now. Will drop the table before putting in real values.

    log_sensor(sensor_name, timestamp, val_raw, val_cal)

def query_SCPI(IP_ADDRESS, PORT, TIMEOUT, SCPI_string):    
    #Establish connection via the socket
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_connection.settimeout(TIMEOUT)
    socket_connection.connect((IP_ADDRESS, PORT))

    # Send encoded message and record time of the measurement
    socket_connection.sendall(SCPI_string.encode())
    timestamp = datetime.datetime.now()

    # Apply recv until a message with a newline at the end is received
    recv_bytes = bytes(0)  # Empty bytes
    while True:
        recv_bytes += socket_connection.recv(4096)
        print(recv_bytes.decode())
        if recv_bytes[-1:] == b"\n":  # Check if last term is a newline
            break

    val_raw = recv_bytes.decode()

    return timestamp, val_raw
    
