from TextUI import *
from blessed import Terminal
import time
import math


class MagnetDisplay:
    def __init__(self):
        self.voltage_tile=TextTile("Voltage: 0.0 V",(0,0,20,3),title="Voltage")
        self.current_tile=ValueTile(0.0,(0,0,20,3),title="Current",units="A")
        self.input_tile=TextEntryTile("",(0,0,20,3),title="Set Voltage")
        self.voltage_gauge=TwoWayHGauge((0,0,20,4),bounds=(-2,2),title="Voltage Gauge")
        self.voltage_plot=TimeGraph((0,0,20,10),title="Voltage Plot",bounds=(-2,2),x_labels=("-2s","0s"))
        self.ui=VStackTile((0,0,20,10),[self.voltage_tile,
                                        self.current_tile,
                                        self.input_tile,
                                        self.voltage_gauge,
                                        self.voltage_plot])

    def update_ui(self,terminal):
        self.ui.draw(terminal)
        

if __name__=="__main__":
    silly_timer=0
    term=Terminal()
    display=MagnetDisplay()
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            silly_timer+=1
            display.voltage_tile.text="{:.2f} V".format(math.sin(silly_timer/20))
            display.voltage_gauge.value=math.sin(silly_timer/20)
            display.voltage_plot.add_data_point(math.sin(silly_timer/20))
            val = term.inkey(timeout=0.1)
            if val:
                if val.name=="KEY_ENTER":
                    break
                display.input_tile.handle_key(val)
            display.update_ui(term)
    term.exit_fullscreen()
