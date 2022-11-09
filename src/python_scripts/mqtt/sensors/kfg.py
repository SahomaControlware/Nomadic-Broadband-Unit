from typing import Optional

import serial
from serial import SerialException
import time
import glob
import yaml


# Reads from rs485 connection
def readMeasuredValues(port):
    try: 
        comPort = serial.Serial(port)  # Port should be a string for the com value
        comPort.baudrate = 115200
        comPort.bytesize = 8
        comPort.parity = "N"
        comPort.stopBits = 1
        dataOut = bytearray(':R50=2,2,1,\r\n', encoding='ascii')
        comPort.write(dataOut)
        dataIn = comPort.read(84)
    except Exception: 
        return None
    return dataIn


# Scan for com ports for RS-485 connection
def checkComs():
    ports = glob.glob('/dev/tty[A-Za-z]*')  # Get list of serials
    totalPorts = []
    for port in ports:
        try:  # Attempt to load serial as a communication port
            s = serial.Serial(port)
            s.close()
            totalPorts.append(port)  # Append if it succeeded
        except (OSError, serial.SerialException):
            # Port is not a valid communications port
            pass
    return totalPorts


class KFG:
    def __init__(self, name: str, port=None, config = None):

        if port == None:
            availablePorts = checkComs()  # Check the available ports
            print(availablePorts)
            if len(availablePorts) == 1 and availablePorts[0] == "/dev/ttyAMA0":  # If there are no possible communication ports, report it
                print("No communication ports found!")
                print("Check drivers and connections")
                self.__name = None
                self.__config = None
                self.__rs485Port = None
                return None
            # Figure out which one is for the RS485 port here...
            rs485Port = availablePorts[0]  # Get the communication port
        else:
# Need error checking here for when we cant get readings from the kfg sensor.!!!! (1)
            rs485Port = port
        self.__name = name
        self.__config = config
        self.__rs485Port = rs485Port
        self.__data = None

    def getData(self, update=True):
        #Keep reading until we get a readable byte array
        if update:
            while True: 
                print("Reading Data...")
                if self.getPort() == '/dev/ttyAMA0' or self.getPort() == '/dev/ttyprintk': 
                    print("ERROR WRONG PORT", self.getPort() )
                    data = None
                    return data 
                else: 
                    serialData = readMeasuredValues(self.getPort()) 
                    #print("READ VALUES:", serialData)
                    data = self.__parse_byte_arr(serialData)
                #print("PARSED DATA:", data) 
                self.__data = data 
                if data != None: 
                    return data
                print('Trying to read again..') 
        else: 
            return self.__data 

    def getName(self):
        return self.__name

    def getConfig(self):
        return self.__config

    def getPort(self):
        return self.__rs485Port
    
    def setConfig(self, config): 
        self.__config = config
        return self.__config

    def __parse_byte_arr(self, byte_arr: bytearray) -> dict:
        if byte_arr == None:
            return None
        if byte_arr.split(b',')[0] != bytearray(b':R50=01.\r\n:r50=1'): 
            print("ERROR: Invalid reading!", byte_arr) 
            return None
        try: 
            data = byte_arr.strip(b':R50=01.\r\n').strip(b'r50=').decode()
        except UnicodeDecodeError:
            print("ERROR: Unicode Decode error, can not decode byte array.", byte_arr)
            return None
        
        data = data.split(',')
        # Just in case we get extra numbers, we only want first 15
        data = data[0:14]
        print(f"Array of data: {data}")
        if len(data) < 13: 
            return None

        readings = {}

        readings['Communication_address'] = data[0]
        readings['Checksum'] = data[1]
        readings['Voltage'] = int(data[2]) / 100  # in V
        readings['Current'] = int(data[3]) / 100  # in A
        readings['Remaining_Capacity'] = int(data[4]) / 1000.00  # in Ah
        readings['Percentage_Left_200Ah'] = (readings.get('Remaining_Capacity') / 200) * 100
        readings['Cumulative_Capacity'] = int(data[5]) / 1000.00  # in Ah
        readings['Watt_hour'] = int(data[6]) / 10000.00  # in kw.h
        readings['Running_Time'] = int(data[7])  # in Seconds
        temp_c = int(data[8])
        # in Celsius
        readings['Ambient_Temp'] = temp_c % 100 if temp_c > 100 else -1  # in Celsius
        readings['Power'] = int(data[9])  # Watts
        status = int(data[10])
        #print(f"status: {status}")
        readings['Output_Status'] = self.__get_output_status(status)
        readings['Current_Direction'] = "DISCHARGING" if data[11] == '0' else "CHARGING"
        readings['Battery_Life'] = int(data[12])  # in minutes
        try:
            readings['Internal_Resistance_Battery'] = int(data[13]) / 100  # in m ohms
        except Exception: 
            readings['Internal_Resistance_Battery'] = "UKNOWN (might be 0)"
        return readings

    def __get_output_status(self, status: int) -> str:
        if status == 0:
            return "ON"
        elif status == 1:
            return "OVP"
        elif status == 2:
            return "OCP"
        elif status == 3:
            return "LVP"
        elif status == 4:
            return "NCP"
        elif status == 5:
            return "OPP"
        elif status == 6:
            return "OTP"
        elif status == 255:
            return "OFF"
        else:
            return "UNKNOWN"
