# reedDaemon
Python Daemon for Raspberry Pi GPIO reed switch

## Hardware
For this project, I used a raspberry Pi 2B, which I was already using for other projects as well ([here](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/ "www.raspberrypi.org")).

Next to that, I used some fancy and very small reed switches, you can easily mount in a door, hidden from view ([here](https://www.dx.com/p/rc-33-5pcs-wired-door-magnetic-reed-switches-alarms-set-white-2084142 "DX.com")).

The reed-switch is connected the GND on one side and to a GPIO pin on the other side (GPIO4 in my case). The GPIO-pin is configured as **input**, with internal **pullup** enabled.

## Software

### Python code
The python code (*reedDaemon.py*) will do the following:
* Configure GPIO
* Configure backgrond timer
* Configure MQTT connection
* check reed state and publish to MQTT broker
    * On GPIO change
    * Periodically

### Watchdog
The watchdoc shell script (*reedDaemon.sh*), will allow you to:
* start
* stop
* restart
* status

When executed with *start* command, the script will start the python code and then fork itself and become the background watchdog. The watchdog code will restart the python code in case it terminates unexpectedly.

### Service
The service unit allows the watchdog to be installed as a *systemd*-service.
