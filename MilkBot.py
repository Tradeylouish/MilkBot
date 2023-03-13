#!/usr/bin/env python

import time

import serial
import serial.tools.list_ports

import pygame
import keyboard

class MilkBot:
    def __init__(self, soundfile):
        # Serial / distance setup
        self.ser = self.setupSerial()
        self.prevDistance = -1.0
        self.simulatedValue = -1.0

        # Pygame audio setup
        pygame.init()
        self.sound = pygame.mixer.Sound(soundfile)
        # Can also use FastMilk.mp3

        # Timestamp for sound interval
        self.timestamp = time.time()

        # Delay before spamming the console
        time.sleep(2)

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
            
        print("Couldn't establish a serial connection, using simulation")
        return None

    def simluateSerial(self):
        # Limit to 0-300 cm
        if keyboard.is_pressed("up arrow"):
            self.simulatedValue = min(300.0, self.simulatedValue + 0.01)
        if keyboard.is_pressed("down arrow"):
            self.simulatedValue = max(0, self.simulatedValue - 0.01)
        
        # Simulate error value at high distance
        if self.simulatedValue == 300.0:
            return "-1.0"
        return str(self.simulatedValue)

    def readSerial(self):
        # Dummy values for no serial
        if self.ser is None:
            return self.simluateSerial()

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

    def calculateVolume(self, distance):
        # Change from half to max volume when getting a valid distance
        if distance < 0:
            return 0.5
        return 1.0

    def calculateInterval(self, distance):
        # 10 second default
        if distance < 0:
            return 10
        
        # Tune the interval
        MIN_INTERVAL = 0.44
        INTERVAL_GRADIENT = 30
        return max(distance/INTERVAL_GRADIENT, MIN_INTERVAL)

    def milkSound(self):
        distance = self.getDistance()

        volume = self.calculateVolume(distance)
        interval = self.calculateInterval(distance)

        print(distance)
        
        timeElapsed = (time.time()-self.timestamp)

        if timeElapsed >= interval:
            self.sound.set_volume(volume)
            self.sound.play()
            self.timestamp = time.time()

    def run(self):
        while 1:
            self.milkSound()

if __name__ == '__main__':
    milk_bot = MilkBot("Sounds/Milk.mp3")
    milk_bot.run()


