#Function for motor commands
import socket

steps_per_second = 

BDP_IP = "192.168.25.3"
TDP_IP = "192.168.25.4"
CM_IP = "192.168.25.5"
port = 7776

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
def motor_command(IP, command_str):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        sock.connect((IP, port))
        header = bytes(([0x00, 0x07]))
        end = bytes([0xD])

        encodeMessage = command_str.encode()
        Send = header + encodeMessage + end
        sock.sendto(Send,(IP,port))

        response = sock.recv(2048)
        #print(f"Motor response: {response.decode('ascii').strip()}")
        return response.decode('ascii').strip()
    except socket.error as err:
        #print(f"Error communicating with motor: {err}")
        return "SOCKET ERROR"
    finally:
        s.close()

def move_motor(motor_name, num_steps):
    IP = select_motor(motor_name)
    
    motor_command(IP, "DI"+str(num_steps))
    motor_command(IP, "FL")
    #time.sleep(np.abs(num_steps)/steps_per_second)
    f = True
    while f:
        steps = motor_command(IP, "SP")
        if steps == "*":
            f = True
        else:
            f = False
    return steps

def reset_motor_suddenly(motor_name):
    IP = select_motor(motor_name)
    motor_command(IP, "RE")

def reset_all_motors_suddenly():
    motor_command(BDP_IP, "RE")
    motor_command(TDP_IP, "RE")
    motor_command(CM_IP, "RE")
