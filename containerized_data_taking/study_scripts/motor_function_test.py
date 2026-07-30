from motor_functions import motor_command, move_motor, coordinated_motion
IP = "192.168.25.5"
motor_command(IP,"EP")
x = coordinated_motion(.5)
print(x)
