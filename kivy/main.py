# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 11:13:37 2014

@author: nick
"""

from kivy.config import Config
Config.set('graphics', 'width', '1280')# set screen size to nexus 7 dimensions looks ok on PC
Config.set('graphics', 'height', '720')
Config.write()
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, BoundedNumericProperty,ListProperty, StringProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.tabbedpanel import TabbedPanel
import re
import os
import glob

import Counter as cm



class FloatInput(TextInput): 

    pat = re.compile('[^0-9]')
    multiline = False
    halign = 'center'

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)

class CounterControl(TabbedPanel):
    counts = StringProperty('0 0 0')
    frequency = NumericProperty(0.0)
    gate_time = BoundedNumericProperty(100, min=1,max=10000,errorhandler=lambda x: 10000.0 if x > 10000 else 1)
    logic_level = StringProperty('Not connected')
    serial = StringProperty('Not connected')
    connected = BooleanProperty(False)
    logo = 'CQTtools_inverted.png'
    graph = Graph()


    plot = ObjectProperty(None)

    counter = None
        
    iteration = 0
    
    dt = 1
    

    def update(self, dt):
        self.gate_time = self.counter.get_gate_time()
        self.counts = self.counter.get_counts()
        self.plot.points.append((self.iteration*dt,self.iteration))
        self.iteration += 1*dt
        if self.iteration > 150:
            self.iteration = 0
            self.plot.points = []
            self.ids.graph1.remove_plot(self.plot)
  

        

    def connect_to_powermeter(self, connection):
        if not self.connected:
            if platform == 'android': #to get access to serial port on android
                os.system("su -c chmod 777 " + connection)#has to run as child otherwise will not work with all su binarys
            self.counter = cm.Countercomm(connection)
            Clock.schedule_interval(self.update, self.dt)
            self.connected = True
            self.serial = self.counter.serial_number()
            self.logic_level = self.counter.get_digital()
            self.counter.set_gate_time(10) # sets gate time to 100ms
            self.gate_time =  float(self.counter.get_gate_time())
            plot = MeshLinePlot(color=[0, 1, 0, 1])
            self.ids.graph1.add_plot(plot)
            self.plot = plot
            
            
    def serial_ports_android(self):
        #Lists serial ports
        portA = glob.glob('/dev/ttyACM*') #finds both serial USB liunx
        portB = glob.glob('/dev/ttyUSB*')
        ports = portA + portB
        return ports 
    
    def update_gate_time(self,gate_time):
        self.gate_time = gate_time
        gate_time_sec = gate_time/1000.0 #convert to seconds
        if gate_time_sec > self.dt:
            self.dt = gate_time_sec
        self.counter.set_gate_time(gate_time)
        return self.gate_time
    
    def set_logic_level(self,level):
        if level == 'NIM':
            self.counter.set_NIM()
        elif level == 'TTL':
            self.counter.set_TTL()
        return
        


class CounterApp(App):
    def build(self):
        control = CounterControl()
      
        return control
    
    def on_pause(self):
        return True
        
    def on_resume(self):
        pass




if __name__ == '__main__':
    CounterApp().run()
