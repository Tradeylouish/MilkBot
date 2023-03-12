#include <Arduino.h>

#include <HCSR04.h>

UltraSonicDistanceSensor distanceSensor(7, 6);  // Initialize sensor that uses digital pins 13 and 12.

void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
}

// the loop routine runs over and over again forever:
void loop() {

  // Print the distance
  float distance = distanceSensor.measureDistanceCm();
  Serial.println(distance);
  delay(500); // Low polling rate to reduce power consumption
}
