from w1thermsensor import W1ThermSensor
import time
import yaml
import datetime

# WE NEED TO ADD ALL GPIO PINS TO A SINGLE GPIO INIT SO WE ONLY NEED TO CALL THE FUNCTION ONCE
# def gpioInit():
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(14, GPIO.IN)  # Temperature Sensor 1
#     GPIO.setup(15, GPIO.IN)  # Temperature Sensor 2
#     GPIO.setup(18, GPIO.IN)  # Temperature Sensor 3
#     GPIO.setup(23, GPIO.IN)  # Temperature Sensor 4

class Sensors:
    def __init__(self, sensor_map, name=None,  debug=False) -> None:
        self.__debug = debug
        self.__temp = {}
        self.__status = {}
        self.__name = name if name != None else "TemperatureSensors"
        #Sensor mapping {'<name of sensor>' : sensorID} ex. {'Room1' : '3c01f096952b'}
        self.__map = dict(sensor_map)

        with open("./config/config.yaml") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
        self.__config = dict(config)
        self.readSensors()
        

    def getConfig(self):
        return self.__config

    def getTemps(self):
        return self.__temp

    def getStatus(self):
        return self.__status

    def getName(self):
        return self.__name

    def readSensors(self):
        temps = {}
        status = {}
        for name, sid in self.__map.items():
            try:
                temp = W1ThermSensor(sensor_id=sid).get_temperature()
            except:
                temp = None
                self.__status = None 
                print("Couldnt get sensor!", name, sid)
                continue
            temps[name] = {'TempC' : temp }
            status[name] = {'Status': "ON" if temp != None else "OFF"}
        if len(temps) == 0: 
            return
        # self.__status = status
        # self.__temp = temps
        # currTime = datetime.datetime.now()
        # month = currTime.strftime("%B")
        # currTime = ("%s %s, %s | %s:%s:%s" %(month, currTime.day, currTime.year, currTime.hour, currTime.minute, currTime.second))
        # self.__temp["time"] = currTime
        # self.__temp["userId"] = "1"
        return temps
