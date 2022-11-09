import RPi.GPIO as GPIO
from time import sleep


class Relay:
    def __init__(self, initalV=GPIO.LOW, warnings=False, mode=GPIO.BCM, name=None):
        try:
            GPIO.setwarnings(warnings)
            GPIO.setmode(mode)
            self.__relayMap = {"1": 5,
                               "2": 6,
                               "3": 13,
                               "4": 16,
                               "5": 19,
                               "6": 20,
                               "7": 21,
                               "8": 26}
            self.__name = "RelayChannels" if name is None else name

            for relay in self.__relayMap:
                GPIO.setup(self.__relayMap.get(relay),
                           GPIO.OUT, initial=initalV)
        except:
            self.__name = None
            return

    def getRelayState(self):
        state = {}
        for relay in self.__relayMap:
            currPin = self.__relayMap.get(relay)
            state[relay] = GPIO.input(currPin)
        return state

    def getName(self):
        return self.__name

    def setRelayState(self, pin_number, state):
        try:
            GPIO.output(self.__relayMap.get(pin_number), state)
        except Exception:
            print("ERROR: Couldnt set gpio pin state")
            return None
        return self.getRelayState()

    def getPins(self):
        return list(self.__relayMap.values())

    def cleanUp(self):
        GPIO.cleanup()


if __name__ == "__main__":
    try:
        relay = Relay()
        sleep(2)
        print(relay.getPins())
        while True:
            print("Current Relay State", relay.getRelayState())

            print("Setting first relay")
            relay.setRelayState("1", 1 if GPIO.input(17) == 0 else 0)
            print("Relay Set!", relay.getRelayState())
            sleep(5)
    except Exception:
        raise

    finally:
        GPIO.cleanup()
