# MilkBot

This was a 2023 [Terrible Ideas Hackathon project](https://terriblehack.com/projects/milk-aromatherapy) which aimed to create the world's leading Milk Aromatherapy device in the space of a few hours.

It involved an aroma diffuser filled with milk and stuffed inside a milk carton, alongside the guts of [MinionBot9000](https://github.com/Tradeylouish/MinionBot9000) stuffed into the Aroma diffuser's box.

The guts in question were a USB power bank, a Raspberry Pi, a speaker, and an Arduino Uno. Where in MinionBot the Arduino provided analog read capabilities for its pain sensing, with readings relayed over USB Serial, in MilkBot this was subsituted for an HC-SR04 ultrasonic distance sensor. The bot would intermittently chant "Milk", and thanks to the distance sensor the pace of the chanting would increase as you approached the carton to take in the smell up close. It mostly just smelt like warm milk, but I like to think that the chanting enhanced the sensory experience.

This repository contains the code for both the Pi and the Arduino, with some minor changes made post-project. However, it's an appropriately janky fork of an even older janky project from 2019, so trying to get this running is not recommended.

![milkbot](img/milkbot.jpg?raw=true)
