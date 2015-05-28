#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 16:45:23 2015

@author: nick
"""

import sys
sys.path.append('../')

import time
import glob
import serial
from PyQt4 import QtGui, uic
from PyQt4.QtCore import QTimer
import pyqtgraph as pg
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
		self.comboLogicBox.currentIndexChanged.connect(self.logic_mode_change)
		self.pen = pg.mkPen(color=(0,0,0), width=2)
		self.plotWidget.plotItem.getAxis('left').setPen(self.pen)
		self.plotWidget.plotItem.getAxis('bottom').setPen(self.pen)
		self.plotWidget.setLabel('left', 'Freq', 'Hz')
		self.plotWidget.setLabel('bottom', 'Time', 'Sec')
		self.plotWidget
		self.freq_samples = []
		self.timedata = []
		
	def ButtonConnect_clicked(self,connection):
		global channel
		global starttime
		global gate_time
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
			starttime = time.time()
			self.count = float(self.counter.get_counts().split(' ')[channel])
			self.freq = float(self.count*1000/self.gate_time)
			self.label_channel.setText(str(1))
			gate_time  = float(self.counter.get_gate_time())
			
					
	def ButtonUpdate_gate_clicked(self,value):
		global gate_time
		self.counter.set_gate_time(str(self.gate_box.text()))
		self.label_gate.setText(str(self.counter.get_gate_time())+" ms")
		print 'gate updated'
		gate_time  = float(self.counter.get_gate_time())
		
	
	def ButtonUpdate_channel_clicked(self,value):
		global channel 
		channel = self.channel_box.text()
		self.label_channel.setText(str(channel))
	
	def logic_mode_change(self):
		self.index = self.comboLogicBox.currentIndex()
		if self.index == 0:
			self.counter.set_NIM()
			print 'set counter to NIM'
		if self.index == 1:
			self.counter.set_TTL()
			print 'set counter to TTL'
		
		
	def update(self):
		self.timer.setInterval(gate_time)
		self.plt = self.plotWidget
		try:
			self.counts = self.counter.get_counts()
			self.count = float(self.counts.split(' ')[channel])
			self.freq = float(self.count*1000/gate_time)
			self.label_count.setText(str(self.count))
			self.label_freq.setText(str(self.freq) +" Hz")
			self.freq_samples.append(self.freq)
			self.time = float("{0:.3f}".format(time.time() - starttime))
			self.timedata.append(self.time)
			self.plt.plot(self.timedata,self.freq_samples,clear=True,pen={'color':'k','width':2})
		except:
			pass
		
		
		

app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
