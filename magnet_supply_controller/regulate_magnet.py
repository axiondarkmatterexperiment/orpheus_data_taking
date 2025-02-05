import sys
import os
sys.path.insert(0,'..')
from monitoring_functions import log_sensor
import datetime
import pytz

from MagnetRegulator import MagnetRegulator
from blessed import Terminal
from MagnetDisplay import MagnetDisplay

term=Terminal()
display=MagnetDisplay()
regulator=MagnetRegulator("magnet_controller_config.yaml")
regulator.start_thread()
with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    while True:
        #update my current
        current=regulator.get_last_current_measurement()
        timestamp=datetime.datetime.now(pytz.timezone('US/Pacific'))
        log_sensor("magnet_measured_current",timestamp,current,current)
        display.set_measured_current(current)
        v=regulator.get_last_ps_voltage()
        display.set_voltage(v)
        display.set_pid(regulator.get_last_p_i_d())
        display.set_set_current(regulator.get_target_current())



        val = term.inkey(timeout=0.1)
        if val:
            if val.name=="KEY_ENTER":
                input_text=display.input_tile.text
                display.input_tile.text=""
                if input_text=="quit":
                    break
                try:
                    set_current=float(input_text)
                    #val=regulator.set_power_supply_voltage(set_current)
                    regulator.set_target_current(set_current)
                    #display.set_set_current(set_current)
                except ValueError:
                    display.message_tile.text="Invalid input"
            else:
                display.input_tile.handle_key(val)
        display.update_ui(term)
regulator.should_quit=True
term.exit_fullscreen()

