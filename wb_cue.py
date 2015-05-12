#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
	wb-cue
	~~~~~~~~~~~~~~~~~~~~

	:author: Gabe Russell <gabe@gaberussell.com>
	:license: LGPL – see license.lgpl for more details.
'''
import threading
import socket
import time, datetime
import struct
import random

import forecastio
from evdev import InputDevice, categorize, ecodes

import wb_config as config

location = None
wCurrently = None
wTomorrow = None

mouseInput = open( "/dev/input/mice", "rb" );

def weatherUpdate():
	print 'Updating weather...'
	forecast = forecastio.load_forecast(config.weather_api_key, config.location[0], config.location[1])

	global wCurrently, wTomorrow

	# if we have a change in forecast, store and update
	if wCurrently != forecast.currently().icon:
		wCurrently = forecast.currently().icon
		sendCue(wCurrently)
	
	if wTomorrow is not forecast.daily().data[0].icon:
		wTomorrow = forecast.daily().data[0].icon

	print "Currently: " + wCurrently
	print "Tomorrow: " + wTomorrow

	
	#setWeatherTimer()

# returns location; at some point this should be auto lat/long from API
def getLocation():
	return config.location

def setWeatherTimer():
	weatherTimer = threading.Timer(600.0, weatherUpdate).start()

def sendCue(cue):
	print "cue"
	x = 0
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	while x < 3:
		try:
			s.connect((config.cue_server_ip, config.cue_server_port))
			s.sendall(cue)
		except:
			print "Can't connect to weatherbox server"
			x += 1
			time.sleep(15)

	s.close()


# def sendRandomCue():
# 	c = random.randint(1,3)
# 	if c is 1:
# 		sendCue('rain')
# 	elif c is 2:
# 		sendCue('snow')
# 	else:
# 		sendCue('clear-day')

# def getMouseEvent():
#   buf = mouseInput.read(3);
#   button = ord( buf[0] );
#   bLeft = button & 0x1;
#   bMiddle = ( button & 0x4 ) > 0;
#   bRight = ( button & 0x2 ) > 0;
#   x,y = struct.unpack( "bb", buf[1:] );
#   print ("L:%d, M: %d, R: %d, x: %d, y: %d\n" % (bLeft,bMiddle,bRight, x, y) );

#   # TODO: concatentate multiple short-term inputs to prevent multiple events from firing
#   if (y > 40):
# 	return 'right'
#   elif (y < 40):
#   	return 'left'

def touchLoop():
	dev = InputDevice('/dev/input/event0')
	while True:
		for event in dev.read_loop():
			if event.type == ecodes.BTN:
				print(categorize(event))	

def startCueClient():
	# get location
	global location
	location = getLocation()

	# init loop to check weather
	weatherUpdate();

	# init loop to take touchscreen input
	# touchThread = threading.Thread(target=touchLoop)
	# touchThread.start()

	# while(True):
	# 	event = getMouseEvent()
	# 	if(event == 'right'):
	# 		sendRandomCue()

if __name__ == '__main__':	
	startCueClient()