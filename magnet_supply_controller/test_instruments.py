from PrologixGPIBConnection import *
from Instruments import *

ip_address="10.168.25.15" #this is the ip address of the prologix controller
power_supply_gpib_address=0 #this is the address of the power supply
voltmeter_gpib_address=3 #this is the address of the voltmeter

connection=PrologixGPIBConnection(ip_address)
connection.connect()

powerSupply=PowerSupply(connection,power_supply_gpib_address)
voltmeter=Voltmeter(connection,voltmeter_gpib_address)

print("configuring power supply")
powerSupply.configure()
print("configuring voltmeter")
voltmeter.configure()

print("setting voltage")
volts=powerSupply.set_voltage(5)
print("voltage is {} volts".format(volts))

print("turning on power supply")
powerSupply.on_off(True)
print("turning off power supply")
powerSupply.on_off(False)

print("Measuring the voltage with the voltmeter")
volts=voltmeter.get_voltage()
print("voltage is {} volts".format(volts))
