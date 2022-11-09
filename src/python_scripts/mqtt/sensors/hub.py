from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QPushButton, QLabel
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import sys
import os
import RPi.GPIO as GPIO
from time import sleep
import relay as rel

class broadbandScreen(QWidget):
	def please():
		print("NO")
'''		
	def paintEvent(self, e):
		painter = QtGui.QPainter(self)
		painter.setPen(QtGui.QPen(Qt.red, 8, Qt.SolidLine))
		painter.setBrush(QtGui.QBrush(Qt.red,  Qt.SolidPattern))
		painter.drawEllipse(100, 100, 40, 40)'''
		
		
	

def main():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	#Each relay channel is mapped to a gpio pin
	#Key -> Relay Channel | Value -> GPIO pin
	relayMap = {"1" : 17, "2" : 27, "3" : 22, "4" : 5, "5" : 6, "6" : 13, "7" : 19, "8" : 26}
	for relay in relayMap: #Initialize each GPIO pin
		GPIO.setup(relayMap.get(relay), GPIO.OUT, initial=GPIO.LOW)
	
	app = QApplication(sys.argv)
	mainWindow = broadbandScreen()
	windowX=720
	windowY=720
	mainWindow.setFixedSize(720, 720)
	mainWindow.setWindowTitle("Mobile Broadband Unit")
	buttList = []
	lightList = []
	for i in range(8):
		relayButton = QPushButton(mainWindow)
		relayButton.setText("Relay Channel " + str(i+1))
		threshold = 0
		x=i+1
		if(i>3):
			threshold=1
			i-=4
		newLabel = QLabel("", mainWindow)
		
		newLabel.resize(40,40)
		newLabel.setStyleSheet("background-color: grey; border: 3px solid grey; border-radius: 20px;")
		lightList.append(newLabel)
		
		relayButton.clicked.connect(lambda skip, x=x, lab=newLabel: rel.toggleRelay(relayMap, str(x), lab))
		buttList.append(relayButton)

		newLabel.move(windowX/16+((windowX/4)*i)+24,(100*threshold)+35)
		relayButton.move(((windowX/4)*i)+32, 100*threshold) 
		

	#mainWindow.paintCircle()
	#painter = QPainter()
	for i in range(8):
		pass	
	
	mainWindow.show()  
	app.exec()


	


if __name__ == "__main__":
	main()
