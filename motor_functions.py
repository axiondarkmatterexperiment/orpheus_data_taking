#Function for motor commands
import socket

BDP_IP = "192.168.25.3"
TDP_IP = "192.168.25.4"
CM_IP = "192.168.25.5"
port = 7776

#physical parameters:
steps_per_cm = 20000#This is incorrect


def select_motor(motor_name):
    if motor_name == "bottom_dielectric_plate":
        IP=BDP_IP
    elif motor_name == "top_dielectric_plate":
        IP=TDP_IP
    elif motor_name == "curved_mirror":
        IP=CM_IP
    else:
        IP="NONE"
    
    return IP 

#Add error handling?
def motor_command(IP,command):
    """Sends a single SCL command and waits for a response."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)  # Set a timeout for the connection
        s.connect((IP,port))

        # SCL commands must be sent as bytes and end with a carriage return
        header = bytes(([0x00, 0x07]))
        end = bytes([0xD])

        send_encoded = header + command.encode() + end
        s.sendto(send_encoded,(IP,port))
        #s.sendall(command.encode() + b'\r')

        # Read and print the motor's response
        response = s.recv(2048)
        return response.decode('ascii').strip()
        print(f"Motor response: {response.decode('ascii').strip()}")

    except socket.error as err:
        print(f"Error communicating with motor: {err}")
    finally:
        s.close()#    try:
#        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        sock.settimeout(5)
#        sock.connect((IP, port))
#
#        header = bytes(([0x00, 0x07]))
#        end = bytes([0xD])
#
#        encodeMessage = command_str.encode()
#        Send = header + encodeMessage + end
#        sock.sendto(Send,(IP,port))
#
#        response = sock.recv(2048)
#        #print(f"Motor response: {response.decode('ascii').strip()}")
#        return response.decode('ascii').strip()
#    except socket.error as err:
#        #print(f"Error communicating with motor: {err}")
#        return "SOCKET ERROR"
#    finally:
#        sock.close()

def coordinated_motion(dl_cm):#dl_cm is the change in cavity length in cm
    

def move_motor(motor_name, num_steps):
    IP = select_motor(motor_name)
    
    motor_command(IP, "DI"+str(num_steps))
    motor_command(IP, "FL")
    #time.sleep(np.abs(num_steps)/steps_per_second)
    f = True
    while f:
        steps = motor_command(IP, "SP")
        steps = steps[2:]#Cuts out the '\x00\x07' at the start of the message
        if steps == "*":
            f = True
        else:
            steps=steps[3:]#Cuts out the 'SP=' at the start of the message
            #try exception because before the motion is complete it returns ?6 instead of step number for a few loops.
            try:
                steps = int(steps)
                print("Motion completed. Total steps = " + str(steps))
                f = False
            except ValueError:
                f = True
    return steps

def reset_motor_suddenly(motor_name):
    IP = select_motor(motor_name)
    motor_command(IP, "RE")

def reset_all_motors_suddenly():
    motor_command(BDP_IP, "RE")
    motor_command(TDP_IP, "RE")
    motor_command(CM_IP, "RE")
