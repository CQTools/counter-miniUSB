# -*- coding: utf-8 -*-
"""
Created on Thu May 14 16:45:23 2015

@author: nick
"""

import sys
sys.path.append('../')

import sys
import glob
import serial
from PyQt4 import QtGui, uic
from PyQt4.QtCore import QTimer

import Counter as cm


form_class = uic.loadUiType("countergui.ui")[0] 

def serial_ports():
    
	"""Lists serial ports
	:raises EnvironmentError:
	On unsupported or unknown platforms
	:returns:
	A list of available serial ports
	"""				
	if sys.platform.startswith('win'):
		ports = ['COM' + str(i + 1) for i in range(256)]
	elif sys.platform.startswith('linux'):
	# this is to exclude your current terminal "/dev/tty"
		ports = glob.glob('/dev/serial/by-id/usb-C*')
	elif sys.platform.startswith('darwin'):
		ports = glob.glob('/dev/tty.*')
	
	else:
		raise EnvironmentError('Unsupported platform')
	
	result = []
	for port in ports:
		try:
			s = serial.Serial(port)
			s.close()
			result.append(port)
		except serial.SerialException:
			pass
	return result
    




class MyWindowClass(QtGui.QMainWindow, form_class):
	connected = bool(False)
	counter = None 
	time = 0


	
	def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)
		self.setupUi(self)
		self.ButtonUpdate_gate.clicked.connect(self.ButtonUpdate_gate_clicked)# Bind the event handlers
		self.ButtonUpdate_channel.clicked.connect(self.ButtonUpdate_channel_clicked)
		self.ButtonConnect.clicked.connect(self.ButtonConnect_clicked)
		self.comboSerialBox.addItems(serial_ports()) #Gets a list of avaliable serial ports to connect to and adds to combo box
		
		
	def ButtonConnect_clicked(self,connection):
		global channel
		if not self.connected:
			self.counter = cm.Countercomm(str(self.comboSerialBox.currentText()))
			self.timer = QTimer()
			self.connected = True
			self.timer.timeout.connect(self.update)
			self.timer.setInterval(100)
			self.timer.start()
			self.control_label.setText('connected to ' + str(self.comboSerialBox.currentText()))
			self.counter.set_gate_time(100) # sets gate time to 100ms
			self.gate_time  = float(self.counter.get_gate_time())
			self.label_gate.setText(str(self.gate_time) +" ms")
			channel = 1
			self.count = float(self.counter.get_counts().split(' ')[channel])
			self.freq = float(self.count*1000/self.gate_time)
			self.label_channel.setText(str(1))
			
					
	def ButtonUpdate_gate_clicked(self,value):
		self.counter.set_gate_time(str(self.gate_box.text()))
		self.label_gate.setText(str(self.counter.get_gate_time())+" ms")
		print 'gate updated'
		
	
	def ButtonUpdate_channel_clicked(self,value):
		global channel 
		channel = self.channel_box.text()
		self.label_channel.setText(str(channel))
		
		
	def update(self):
		self.gate_time  = float(self.counter.get_gate_time())
		print channel
		self.timer.setInterval(self.gate_time)
		self.count = float(self.counter.get_counts().split(' ')[channel])
		self.freq = float(self.count*1000/self.gate_time)
		self.gate_time  = float(self.counter.get_gate_time())
		self.label_count.setText(str(self.count))
		self.label_freq.setText(str(self.freq) +" Hz")
		
		
		

app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()