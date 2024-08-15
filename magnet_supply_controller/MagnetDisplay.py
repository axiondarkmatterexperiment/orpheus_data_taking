from TextUI import *
from blessed import Terminal
import time
import math
import random

class MagnetDisplay:
    def __init__(self):
        self.voltage_tile=ValueTile(0.0,(0,0,20,4),title="Supply V",units="V")
        self.current_tile=ValueTile(0.0,(0,0,20,4),title="Magnet Current",units="A")
        self.set_current_tile=ValueTile(0.0,(0,0,20,4),title="Magnet Set Current",units="A")
        self.voltage_gauge=TwoWayHGauge((0,0,20,4),bounds=(-2,2),title="Supply V")
        self.current_plot=TimeGraph((0,0,40,20),title="Magnet Current",bounds=(0,10),x_labels=("-1m","0m"))
        self.p_plot=TimeGraph((0,0,13,20),title="P",bounds=(-0.2,0.2),x_labels=("-10s","0m"))
        self.i_plot=TimeGraph((0,0,13,20),title="I",bounds=(-0.2,0.2),x_labels=("-10s","0m"))
        self.d_plot=TimeGraph((0,0,13,20),title="D",bounds=(-0.2,0.2),x_labels=("-10","0m"))
        self.input_tile=TextEntryTile("",(0,0,40,4),title="Input")
        self.message_tile=TextTile("",(0,0,40,4),title="Message")
        self.ui=VStackTile((0,0,80,24),[HStackTile((0,0,80,4),[self.current_tile,
                                                               self.set_current_tile,
                                                                self.voltage_tile,
                                                                self.voltage_gauge]),
                                        HStackTile((0,0,80,16),[self.current_plot,
                                                                self.p_plot,
                                                                self.i_plot,
                                                                self.d_plot]),
                                        HStackTile((0,0,80,4),[self.input_tile,
                                                                self.message_tile])])
        self.last_current_plot_update_time=time.time()
        self.current_plot_dt=60/(self.current_plot.rect[2]-2)
        self.pid_plot_update_time=time.time()
        self.pid_plot_dt=10/(self.p_plot.rect[2]-2)

    def update_ui(self,terminal):
        self.ui.draw(terminal)

    def set_set_current(self,current):
        self.set_current_tile.set_value(current)

    def set_measured_current(self,current,at_time=None):
        self.current_tile.set_value(current)
        if time.time()-self.last_current_plot_update_time>self.current_plot_dt:
            self.current_plot.add_data_point(current)
            self.last_current_plot_update_time=time.time()

    def set_voltage(self,voltage):
        self.voltage_tile.set_value(voltage)
        self.voltage_gauge.set_value(voltage)

    def set_pid(self,pid):
        if time.time()-self.pid_plot_update_time>self.pid_plot_dt:
            self.pid_plot_update_time=time.time()
            self.p_plot.add_data_point(pid[0])
            self.i_plot.add_data_point(pid[1])
            self.d_plot.add_data_point(pid[2])
        

if __name__=="__main__":
    silly_timer=0
    term=Terminal()
    display=MagnetDisplay()
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            silly_timer+=1
            display.set_voltage(math.sin(silly_timer/20))
            display.set_measured_current(50*(1.0+math.sin(silly_timer/100)))
            display.set_pid(random.gauss(mu=0,sigma=0.1),random.gauss(mu=0,sigma=0.1),random.gauss(mu=0,sigma=0.1))

            val = term.inkey(timeout=0.1)
            if val:
                if val.name=="KEY_ENTER":
                    input_text=display.input_tile.text
                    display.input_tile.text=""
                    if input_text=="quit":
                        break
                    try:
                        set_current=float(input_text)
                        display.set_set_current(set_current)
                    except ValueError:
                        display.message_tile.text="Invalid input"
                display.input_tile.handle_key(val)
            display.update_ui(term)
    term.exit_fullscreen()
