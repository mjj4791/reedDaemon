#!/usr/bin/env python3

import RPi.GPIO as GPIO
from threading import Timer,Thread,Event
import socket
import paho.mqtt.client as mqtt

########################################
# CONFIG:
PIN=4	#GPIO pin to use as input
########################################

print("########################################################")
print("#                      ReedDaemon                      #")
print("#                                                      #")
print("# Version 1.0 (20190530)                               #")
print("#                                                      #")
print("# Changes                                              #")
print("# 1.0 20190530  Initial version                        #")
print("########################################################")

########################################
# Module level variables:              #
########################################
# timer instance for periodic mqtt updates:
timer=None
mqttClient=None                         # mqtt client instance
hostname = socket.gethostname()         # hostname of this device
mqttHost = "10.0.0.2"                   # mqtt server host
mqttPort =  1883                        # mqtt port number
mqttKeepalive = 60                      # mqtt port number
mqttTopic = "%s/door" % (hostname)      # host based topic
mqttLWTTopic = "%s/LWT" % (hostname)    # host based LWT topic
mqttPayloadOpen = "OPEN"                # Open palyload
mqttPayloadClosed = "CLOSED"            # Closed payload
mqttLWTOnline = "ONLINE"                # LWT Online payload
mqttLWTOffline = "OFFLINE"              # LWT Offline payload

timeout = 300                           # timeout of background update timer
########################################

########################################
# Class PerpetualTimer                 #
# continuous timer events              #
########################################
class PerpetualTimer():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()


#######################################
# setupMqtt                           #
# Setup the mqtt connecti             #
#######################################
def setupMqtt():
    global hostname, mqttHost, mqttPort, mqttLWTTopic, mqttLWTOffline
    global mqttClient, mqttTopic, mqttPayloadOpen, mqttPayloadClosed

    print("###############################")
    print("Setup Mqtt as: ", hostname)
    print("MQTT broker: %s:%s" % (mqttHost, mqttPort))
    print("Mqtt topic: ", mqttTopic)
    print("Payload open/closed: ", mqttPayloadOpen, "/", mqttPayloadClosed)
    print("LWT topic: ", mqttLWTTopic)
    print("###############################")

    mqtt.Client.connected_flag = False          # create flag in class
    mqttClient = mqtt.Client(hostname)          # set ouR id
    mqttClient.on_connect = onMqttConnect       # bind call back function
    mqttClient.on_disconnect = onMqttDisconnect # bind call back function

    mqttClient.will_set(mqttLWTTopic, mqttLWTOffline, qos = 1, retain = True)
    mqttClient.loop_start()

#######################################
# connectMqtt                         #
# Connect to mqtt broker.             #
#######################################
def connectMqtt():
    global mqttClient
    global mqttHost, mqttPort, mqttKeepalive

    print("Connecting to broker: %s:%s " % (mqttHost, mqttPort))
    mqttClient.connected_flag = False                           # set flag
    mqttClient.connect(mqttHost, mqttPort, mqttKeepalive)       # connect to broker

#######################################
# sendMqtt                            #
# Send an mqtt message.               #
#######################################
def sendMqtt(topic, payload):
    global mqttClient, mqttTopic

    if mqttClient.connected_flag == False:
        connectMqtt()                                           # not yet connected, so connect and try publish:

    try:
        # connected?, so publish:
        mqttClient.publish(topic, payload, qos = 0, retain = True)  #publish
    except Exception:
        print("Not yet connected? Skipping message...")

#######################################
# sendMqttOnline                      #
# Send an mqtt LWT message.           #
#######################################
def sendMqttOnline():
    global mqttClient, mqttLWTTopic, mqttLWTOnline

    # publish online status:
    mqttClient.publish(mqttLWTTopic, mqttLWTOnline, qos = 0, retain = True)

#######################################
# onMqttDisconnect                    #
# Callback called when mqtt client    #
# disconnects from the mqtt broker.   #
#######################################
def onMqttDisconnect(client, userdata, rc):
    print("Disconnecting reason  "  + str(rc))
    client.connected_flag = False
    #client.disconnect_flag = True

#######################################
# onMqttConnect                       #
# Callback called when mqtt client    #
# connects to the mqtt broker.        #
#######################################
def onMqttConnect(client, userdata, flags, rc):
    global mqttLWTTopic, mqttLWTOnline

    if rc==0:
        client.connected_flag = True #set flag
        print("connected OK")

        sendMqttOnline()
        readState()
    else:
        print("Bad connection Returned code=", rc)
        client.connected_flag = False #set flag

#######################################
# setupGPIO                           #
# Setup GPIO pins                     #
#######################################
def setupGPIO():
    print("Setting up GPIO4 as input with pull-up....")
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)  				# the pin numbers refer to the GPIO numbers on the chip
    GPIO.setup(PIN, GPIO.IN, GPIO.PUD_UP) 	# set up pin ?? (one of the above listed pins) as an input with a pull-up resistor

    # when a falling edge is detected on the input port, the door is closing
    GPIO.add_event_detect(PIN, GPIO.BOTH, callback = doorMoving, bouncetime = 300)

#######################################
# setupTimer                          #
# Setup background timer for timed    #
# updates to mqtt topic.              #
#######################################
def setupTimer():
    global timer, timeout

    print("Setup timer...")
    timer = PerpetualTimer(timeout, onBackgroundTimer)
    timer.start()                           # After 30 seconds, "Alarm!" will be printed

#######################################
# doorMoving                          #
# Callback triggered by changing GPIO #
#######################################
def doorMoving(channel):
    readState()
    return

#######################################
# readState                           #
# Read GPIO pin state                 #
#######################################
def readState():
    global mqttClient, mqttTopic, mqttPayloadOpen, mqttPayloadClosed

    if GPIO.input(PIN):
        print("Switch is open")
        topic = mqttPayloadOpen
    else:
        print("Switch is closed")
        topic = mqttPayloadClosed

    sendMqtt(mqttTopic, topic)


#######################################
# timeout                             #
# Callback for background timer       #
#######################################
def onBackgroundTimer():
    print("Timer elapsed...")
    if mqttClient.connected_flag == True:
        sendMqttOnline()                # repeat LWT online message, for late connected subscribers

    readState()                         # read and update state

#######################################
# main                                #
# Main application loop               #
#######################################
def main():
    global timer

    print("Start reedDaemon main loop...")
    try:
        setupGPIO()
        setupTimer()
        setupMqtt()
        readState()
        while True:
            pass # your code
    except KeyboardInterrupt:
        pass
    finally:
        print("Cleaning up....")
        GPIO.remove_event_detect(PIN)
        GPIO.cleanup(PIN)

        timer.cancel()        # We might just cancel the timer

        print("done.")


if __name__ == '__main__':
    main()
