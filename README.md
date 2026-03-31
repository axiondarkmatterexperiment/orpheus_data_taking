# orpheus data taking
This is the full Orpheus DAQ, run on NLWYMMD, with the digitizer being run on MTTHW.

The final version of the DAQ is in the containerized_data_taking directory.
To run this, enter that directory and execute the command "docker compose up -d --build" or just "docker compose up -d" if there haven't been any changes made to the scripts.

To control the data taking, run terminal_gui.py. This will open up a DAQ interface in the terminal you run the script in. It controls the data taking variables in the docker container through the use of an API, which is defined in control_api.py.

Current problems are:
1. I think that my SCPI commands for the VNA are inefficient. It takes about six seconds for the trigger to be set, sweep settings to be configured, averages to be cleared, etc. The sweep itself takes less than a second. This just feels like I'm doing something wrong.
2. There are occasional instances where the NA scans aren't taken, and then whatever was already on the VNA is logged. This leads to reflection measurements being logged as transmission and vice-versa, as well as reflection measurements being fitted as transmission measurements and vice-versa. This seems to happen about 1% of the time, so it's not a crucial issue.
3. The temperature sensor logging is not yet incorporated into the DAQ.
4. I have seen some digitizations with less than 1024 bins. It doesn't seem to be a problem right now, but I'm not sure why it was ever a problem.

# Hardware notes:

The muxer is an AG34970A which is located on the Orpheus DAQ rack with an HP 34901A muxer plug-in module installed in it.
It has a prologix ethernet to GPIB (same thing as an HP-IB) controller with ethernet port 192.168.25.11 which is how we communicate to it.
We use SCPI commands to communicate with the AG34970A.

The LHe sensor also uses SCPI commands. Its address is 192.168.25.13

The VNA is made by Keysight and can be accessed via remote desktop. Its IP address is 192.168.25.7. Its username is Instrument and its password is measure4u.
