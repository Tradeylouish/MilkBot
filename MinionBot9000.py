#!/usr/bin/env python

from time import sleep
from subprocess import Popen
import os

from datetime import datetime

# Figure out the platform and filepath
import platform
soundspath = "Sounds/"

# Check if it's an RPI
RPi =  platform.uname().node == "raspberrypi"

if RPi:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    from mpu6050 import mpu6050
    from smbus import SMBus
    from bmp280 import BMP280



    print("Running on Raspberry Pi, GPIO enabled")
else:
    print("Running on a non-Pi OS")

import cv2
import numpy as np
import imutils
from collections import deque

import serial
import serial.tools.list_ports

import pygame
# Pygame audio setup
pygame.init()
pygame.mixer.init()

class MinionBot:
    def __init__(self):

        self.lastmilksound = "Milk5times.mp3"
        pygame.mixer.music.load(soundspath + "Milk5times.mp3")
        self.ser = self.setupSerial()

        # Timer for milk frequency
        self.timestamp = datetime.now()
        # Connect to camera
        self.cameraConnected = False

        self.WIDTH = 200
        if self.cameraConnected: self.cam=cv2.VideoCapture(0)

        #banana_cascade = cv2.CascadeClassifier('BananaCascade.xml')
        self.banana_cascade = cv2.CascadeClassifier('banana_classifier.xml')

        self.MIN_BANANA_FRAMES = 5
        self.bananaFrameCount = 0

        # Connect to accelerometer and bmp280 - add a check if connect successful?
        self.accelConnected = False
        self.bmp280Connected = False

        self.accel = None
        self.bmp280 = None

        # Connect to accelerometer
        if RPi and self.accelConnected and  self.accelConnected: self.accel = mpu6050(0x68)

        # Connect to pressure sensor 
        if RPi and self.bmp280Connected:  (self.bmp280, self.baseline) = self.setupBmp280()
            
           

    def setupBmp280(self):
        bus = SMBus(1)
        bmp280 = BMP280(i2c_dev=bus)

        # Check if failed
        if bmp280 is None:
            return None

        baseline_values = []
        baseline_size = 100
        print("Collecting baseline values for {:d} seconds. Do not move the sensor!\n".format(baseline_size/10))

        for i in range(baseline_size):
            pressure = bmp280.get_pressure()
            baseline_values.append(pressure)
            sleep(0.1)

        baseline = sum(baseline_values[:-25]) / len(baseline_values[:-25])

        return bmp280, baseline

    def setupSerial(self):
        # Serial setup - hacky fix for finding Arduino
        ser = None
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
        # "USB" for CH340 serial driver, "ACM" for Atmel driver
            if "USB" in p.device or "ACM" in p.device:
                ser = serial.Serial(p.device,9600)
                print("Established serial connection with " + p.device)
                ser.flushInput()
                break
        return ser

    def readSerial(self):
        # Read analog voltage over serial
        if (self.ser.inWaiting()>0):
            # Read line over serial, strip whitespace and decode
            msg = self.ser.readline()
            msg = msg.strip()
            msg = msg.decode('utf-8')
            try:
                distance = float(msg)
                #print(distance)
                
                volume = 0.5
                interval = 10 # 10 second default interval
                milksound = "Milk.mp3"

                if distance > 0:
                    volume = 1.0
                    # Around 3.3 seconds when at 100cm
                    interval = distance/30
                    print(interval)
                    if interval < 3: milksound = "Milk5times.mp3"

                if milksound is not self.lastmilksound and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(soundspath + milksound)

                # and

                if (datetime.now()-self.timestamp).seconds >= interval:
                    print("Milk!")
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_volume(volume)
                    self.timestamp = datetime.now()
                    
                    
                self.lastmilksound = milksound


            except ValueError:
                print('Not a float')

    def readAccelerometer(self):
        accelerometer_data = self.accel.get_accel_data()
        #print(accelerometer_data)

    def readAltitude(self):
        try:
            altitude = self.bmp280.get_altitude(qnh=self.baseline)
            print('Relative altitude: {:05.2f} metres'.format(altitude))
        except Exception:
            print("IO error")

    def readCamera(self):
        ret, frame = self.cam.read()
        frame = imutils.resize(frame, self.WIDTH)
            
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        #gray = cv2.GaussianBlur(gray, (5, 5), 0)
        gray = cv2.medianBlur(gray,5)
        
        #bananas = banana_cascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=340, minSize=(55, 55))
        bananas = self.banana_cascade.detectMultiScale(gray,scaleFactor=1.05,minNeighbors=4, minSize=(40, 40))
    
        for (x,y,w,h) in bananas:
            print((x,y))
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,0), 2)
            #soundPlayer.playSound('Banana')
        
        if list(bananas):
            self.bananaFrameCount += 1
            if self.bananaFrameCount >= self.MIN_BANANA_FRAMES and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(soundspath + "Banana.mp3")
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(0.6)
        else:
            self.bananaFrameCount = 0
        
        cv2.imshow('frame',frame)

    def run(self):
        while 1:
            if self.ser is not None: self.readSerial()
            if self.accelConnected: self.readAccelerometer()
            if self.bmp280Connected: self.readAltitude()
            if self.cameraConnected: self.readCamera()

            if cv2.waitKey(1) == 27:
                cv2.destroyAllWindows()
                break  # esc to quit
        cv2.destroyAllWindows()


minion_bot = MinionBot()
minion_bot.run()


