import kfg
import serial
import time
import glob
import crc
from serial.tools import list_ports

def readSmartGen(port):
    comPort = serial.Serial(port)  # Port should be a string for the com value
    comPort.baudrate = 9600
    comPort.bytesize = 8
    comPort.parity = "N"
    comPort.stopBits = 1
    dataOut = bytearray(':R50=2,2,1,\r\n', encoding='ASCII')
    print(dataOut)
    comPort.write(dataOut)
    dataIn = comPort.read(64)
    return dataIn

ports = list_ports.comports() #Function to get list of available comports
smartGenPort = ports[1]
readSmartGen = readSmartGen(smartGenPort)
