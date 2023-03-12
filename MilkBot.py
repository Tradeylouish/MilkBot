#!/usr/bin/env python

from time import sleep
import time

from datetime import datetime

# Figure out the platform and filepath
import platform
soundspath = "Sounds/"

# Check if it's an RPI
# RPi =  platform.uname().node == "raspberrypi"

import serial
import serial.tools.list_ports

import pygame
# Pygame audio setup
pygame.init()
pygame.mixer.init()


class MilkBot:
    def __init__(self):

        self.prevDistance = -1.0

        self.sound = pygame.mixer.Sound("Sounds/Milk.mp3")

        self.ser = self.setupSerial()

        # Timer for milk frequency
        self.timestamp = time.time()

    def setupSerial(self):
        # Serial setup - hacky fix for finding Arduino
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
        # "USB" for CH340 serial driver, "ACM" for Atmel driver
            if "USB" in p.device or "ACM" in p.device:
                ser = serial.Serial(p.device,9600)
                print("Established serial connection with " + p.device)
                ser.flushInput()
                return ser
            
        print("Couldn't establish a serial connection, using dummy values")
        return None

    def readSerial(self):
        # Dummy value for no serial
        if self.ser is None:
            return -1.0

        # Read number over serial
        if (self.ser.inWaiting()>0):
            # Read line over serial, strip whitespace and decode
            msg = self.ser.readline()
            msg = msg.strip()
            msg = msg.decode('utf-8')
            return msg
        
        return None

    def getDistance(self):

        msg = self.readSerial()

        # If there's no new serial message, just use the last distance value
        if msg is None:
            return self.prevDistance

        try:
            distance = float(msg)
        except ValueError:
            # If it's not a float, use -1.0 as error value
            distance = -1.0
        
        self.prevDistance = distance
        return distance

    def milkSound(self):
        
        distance = self.getDistance()
        
        volume = 0.5
        interval = 10 # 10 second default interval

        if distance > 0:
            volume = 1.0
            # Around 3.3 seconds when at 100cm

            # Tune the minimum interval based on specific sound
            interval = max(distance/30, 0.44)
        
        #print(interval)
        timeElapsed = (time.time()-self.timestamp)
        print(timeElapsed)

        if timeElapsed >= interval:
            #print("Milk!")
            self.sound.set_volume(volume)
            self.sound.play()
            self.timestamp = time.time()

    def run(self):
        while 1:
            self.milkSound()

if __name__ == '__main__':
    milk_bot = MilkBot()
    milk_bot.run()


