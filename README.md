# orpheus_magnet_test
This is for running a very pared-down Orpheus DAQ. 

I avoid dripline and just run a bunch of python scripts to control the DAQ and save the data.

The magnet test only requires the ag34970a muxer, the LHe level sensor, and the magnet current supply. My aim is to have these store their measured values in a PSQL table which is run locally on NLWYMMD.
