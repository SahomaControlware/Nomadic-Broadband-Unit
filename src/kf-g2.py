

import serial
from serial import SerialException
import time
import glob
import serial.rs485
#Reads from rs485 connection
def readMeasuredValues(port):
    comPort = serial.Serial(port) #Port should be a string for the com value
#    comPort.rs485_mode = serial.rs485.RS485Settings(False, True)
    readCmd = ":R50=2,2,1,"    
    comPort.baudrate = 115200
    comPort.bytesize = 8
    comPort.parity = "N"
    comPort.stopBits = 2
#    dataOut = readCmd
    dataOut = bytearray(b'\0x3A\0x52\0x35\0x30\0x3D\0x32\0x2C\0x32\0x2C\0x31\0x2C\0x0D\0x0A')
    comPort.write(dataOut)
    dataIn = comPort.read(64)
    return dataIn

#Scan for com ports for RS-485 connection
def checkComs():
    ports = glob.glob('/dev/tty[A-Za-z]*') #Get list of serials
    totalPorts = []
    for port in ports:
        try: #Attempt to load serial as a communication port
            s = serial.Serial(port)
            s.close()
            totalPorts.append(port) #Append if it succeeded
        except (OSError, serial.SerialException):
            #Port is not a valid communications port
            pass
    return totalPorts

def main():
    availablePorts = checkComs() #Check the available ports
    #print(availablePorts)
    if(len(availablePorts)==0): #If there are no possible communication ports, report it
        print("No communication ports found!")
        print("Check drivers and connections")
        return
    #Figure out which one is for the RS485 port here...
    rs485Port = availablePorts[0] #Get the communication port
    while True:
        readData = readMeasuredValues(rs485Port) #Read the port from the protocol
        readData_str = ' '.join(format(x, '02x') for x in readData)
        print(readData)

    #print("Data read is :", readData)

if __name__ == "__main__":
    main()
