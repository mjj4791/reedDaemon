import RPi.GPIO as GPIO
import time

########################################
# CONFIG:
PIN=4	#GPIO pint to use as input
########################################

print("########################################################")
print("#                  Reed switch tester                  #")
print("#                                                      #")
print("# Version 1.0 (20190530)                               #")
print("#                                                      #")
print("# Changes                                              #")
print("# 1.0 20190530  Initial version                        #")
print("########################################################")

print("Setting up GPIO4 as input with pull-up....")
GPIO.setmode(GPIO.BCM)  				# the pin numbers refer to the GPIO numbers on the chip
GPIO.setup(PIN, GPIO.IN, GPIO.PUD_UP) 	# set up pin ?? (one of the above listed pins) as an input with a pull-up resistor

print("Looping...")
while True:
	if GPIO.input(PIN):
		print("Switch is open")
	else:
		 print("Switch is closed")
	time.sleep(1)
	