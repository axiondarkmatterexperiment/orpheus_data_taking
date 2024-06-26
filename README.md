# orpheus_magnet_test
This is for running a very pared-down Orpheus DAQ. 

I avoid dripline and just run a bunch of python scripts to control the DAQ and save the data.

The magnet test only requires the ag34970a muxer, the LHe level sensor, and the magnet current supply. My aim is to have these store their measured values in a PSQL table which is run locally on NLWYMMD.

The muxer is an AG34970A which is located on the Orpheus DAQ rack with an HP 34901A muxer plug-in module installed in it.
It has a prologix ethernet to GPIB (same thing as an HP-IB) controller with ethernet port 192.168.25.11 which is how we communicate to it.
We use SCPI commands to communicate with the AG34970A.

The LHe sensor also uses SCPI commands. Its address is 192.168.25.13

I have not physically set up the power supply yet.