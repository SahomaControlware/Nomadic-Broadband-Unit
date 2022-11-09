import time
import serial
import time
import glob
import RPi.GPIO as GPIO

west = 5 #O1A
east = 6 #O1B
up = 13 #O2A
down = 19 #O2B

#This will override the default behavoir of the solar panel controller
#When a pin is pulled to ground it will no longer control the motor
#Take note of the speed of the motor to determine how far it will pan
#and how quickly. Can determine solar panel position from this
def controller():
    print("The available commands are west, east, up and down")
    controls = {"west" : west, "east": east, "up": up, "down": down}
    pinList = [west, east, up, down]
    while(True):
        userInput = input() #Get current direction
        if(userInput == "exit"): #User wants to leave program
            return
        if(userInput in controls): #If the pin is one of the configurable pins
            currDir = controls.get(userInput) #Get the numerical value of the pin
            print("Moving " + str(currDir))
            moveDir(pinList, currDir) #Turn everything but that pin off, desired pin on

        else:
            print("Invalid Direction")
            continue

#This ensures that only one pin can be activated at a time
#It can potentially blow up the circuit if there is more than one
#motor spinning, otherwise you have to split the 5V across the directions
def moveDir(pins, activatePin):
    #Turn the rest of the pins off (override), but activate the desired pin
    for pin in pins:
        if pin==activatePin: #Turn on the desired pin
            GPIO.output(pin, GPIO.HIGH)
        else: #Ovverride the controls for the other one
            GPIO.output(pin, GPIO.LOW)


def gpioInit():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(west, GPIO.OUT, initial=GPIO.LOW) #Override controller
    GPIO.setup(east, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(up, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(down, GPIO.OUT, initial=GPIO.LOW)

def main():
    #gpioInit()
    controller()

if __name__ == "__main__":
    main()
