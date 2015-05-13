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
import syslog
import sys

import forecastio
from evdev import InputDevice, categorize, ecodes

import wb_config as config

wCurrently = None
wTomorrow = None
demoIndex = 0
cueList = ( "CLEAR_DAY",
			"CLEAR_NIGHT",
			"RAIN",
			"SNOW",
			"WIND",
			"FOG",
			"CLOUDY",
			"PARTLY_CLOUDY_DAY",
			"PARTLY_CLOUDY_NIGHT")



# mouseInput = open( "/dev/input/mice", "rb" );

def weatherUpdate():
	log('Updating weather...')
	forecast = forecastio.load_forecast(config.weather_api_key, config.location[0], config.location[1])

	global wCurrently, wTomorrow

	# if we have a change in forecast, store and update
	if wCurrently != forecast.currently().icon:
		wCurrently = forecast.currently().icon
		sendCue(wCurrently)
	
	if wTomorrow is not forecast.daily().data[0].icon:
		wTomorrow = forecast.daily().data[0].icon

	log("Currently: " + wCurrently)
	log("Tomorrow: " + wTomorrow)

	#setWeatherTimer()


# start timer for next cheack of weather
def setWeatherTimer():
	log("Setting timer for next weather update")
	weatherTimer = threading.Timer(600.0, weatherUpdate).start()

# sends a cue to the weatherbox Processing app to change to a different view
def sendCue(cue):
	# set up socket
	x = 0

	# try up to 3 times to connect
	while x < 3:
		x += 1
		try:
			log("Connecting to weatherbox server")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((config.cue_server_ip, config.cue_server_port))
			s.sendall(cue)
			x = 3
			log("Sent cue: " + cue)
		except:
			log("Socket connection error")
			time.sleep(15)
		finally:
			s.close()


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
				log(categorize(event))
				demoCycle();

# convenience function to allow cycling through all possible cues
def demoCycle():
	global demoIndex

	if demoIndex < len(cueList):
		sendCue(cueList[demoIndex])
		demoIndex += 1
	else:
		demoIndex = 0
		sendCue(cueList[demoIndex])		


# convenience function to route logs to a destination
def log(msg):
	syslog.syslog("WB-CUE: " + msg)

def startCueClient():

	while (True):
		demoCycle()
		time.sleep(10)

	# init loop to check weather
#	weatherUpdate();

	# init loop to take touchscreen input
	# touchThread = threading.Thread(target=touchLoop)
	# touchThread.start()

	# while(True):
	# 	event = getMouseEvent()
	# 	if(event == 'right'):
	# 		sendRandomCue()

if __name__ == '__main__':	
	startCueClient()