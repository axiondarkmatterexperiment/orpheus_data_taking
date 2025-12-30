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
        s.close()

def coordinated_motion(dl_cm):#dl_cm is the change in cavity length in cm
    #We aim for even spacing between all of the dielectric plates and the mirrors
    #We assume that we begin in an evenly-spaced configuration
    BDP_ratio = 4/5
    TDP_ratio = 1/5

    #Threaded rods are 20 threads per inch
    #There are 2.54 cm per inch
    #So it is 7.87401574803 threads per cm, which is 0.127 cm per thread
    #A single motor revolution is one thread
    #A single motor revolution is therefore .127 cm
    #A single revolution of the motor is 20,000 steps
    #The conversion is 157480.314961 steps per cm.
    steps_per_cm = 20000/0.127 #This is 157480.314961 steps per cm
    CM_steps = int(dl_cm*steps_per_cm)
    BDP_steps = int(CM_steps*BDP_ratio)
    TDP_steps = int(CM_steps*TDP_ratio)

    motor_command(BDP_IP,"DI"+str(BDP_steps))
    motor_command(TDP_IP,"DI"+str(TDP_steps))
    motor_command(CM_IP,"DI"+str(CM_steps))

    motor_command(BDP_IP,"FL")
    motor_command(TDP_IP,"FL")
    motor_command(CM_IP,"FL")

    BDP_steps = wait_for_motor("bottom_dielectric_plate")
    TDP_steps = wait_for_motor("top_dielectric_plate")
    CM_steps = wait_for_motor("curved_mirror")

    return BDP_steps, TDP_steps, CM_steps
   
def move_motor_cm(motor_name, move_cm):
    if motor_name == "bottom_dielectric_plate" or motor_name == "BDP":
        motor_IP = BDP_IP
    elif motor_name == "top_dielectric_plate" or motor_name == "TDP":
        motor_IP = TDP_IP
    elif motor_name == "curved_mirror" or motor_name == "CM":
        motor_IP = CM_IP
    else:
        print("invalid motor name. Choose either bottom_dielectric_plate, top_dielectric_plate, or curved_mirror, or the initials of any of these.")
        break
    steps_per_cm = 20000/0.127
    steps = int(move_cm*steps_per_cm)
    motor_command(motor_IP,"DI"+str(steps))
    motor_command(motor_IP,"FL")
    wait_for_motor(motor_name)

def wait_for_motor(motor_name):#Waits for the motor to stop turning and then returns the current number of steps in the motor register (how many steps it has moved cumulatively since last reset)
    IP = select_motor(motor_name)
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
                #print("Motion completed. Total steps = " + str(steps))
                f = False
            except ValueError:
                f = True
    return steps

    
def move_motor(motor_name, num_steps):
    IP = select_motor(motor_name)
    
    motor_command(IP, "DI"+str(num_steps))
    motor_command(IP, "FL")
    steps = wait_for_motor(motor_name)
    return steps

def reset_motor_suddenly(motor_name):
    IP = select_motor(motor_name)
    motor_command(IP, "RE")

def reset_all_motors_suddenly():
    motor_command(BDP_IP, "RE")
    motor_command(TDP_IP, "RE")
    motor_command(CM_IP, "RE")
