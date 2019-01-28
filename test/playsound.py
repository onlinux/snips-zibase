#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele 2018
# http://blog.onlinux.fr
# https://github.com/eclipse/paho.mqtt.python#single
#
# Import required Python libraries
import paho.mqtt.publish as publish
SITE = "default"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
SOUNDFILE = "./ia_ora-notification.wav"
binaryFile = open(SOUNDFILE, mode='rb')
wav = bytearray(binaryFile.read())

publish.single("hermes/audioServer/{}/playBytes/whateidver".format(SITE),
               payload=wav, hostname=MQTT_IP_ADDR,client_id="",)
