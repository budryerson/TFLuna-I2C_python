'''=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# File Name: tfli2c_test.py
# Inception: 12 JUL 2021
# Developer: Bud Ryerson
# Version:   0.0.1
# Last work: 12 JUL 2021

# Description: Python script to test the Benewake TFLuna
# time-of-flight Lidar ranging sensor in I2C mode
# using the 'tfli2c' module in development.

# Default settings for the TFLuna is a 0x10 I2C address
# and a 100Hz measurement frame rate. The device will return
# three measurement datums as commanded:
#   Distance in centimeters,
#   Signal strength in arbitrary units and
#   Temperature encoded for degrees centigrade

# 'begin( port, address)' must be called to set the
# I2C port number and address.  This tests the existence
# of the port and address, and returns a boolean result.
# Continuous ranging is not recommended in I2C mode and so
# this function also sets the device to single sample mode.
# NOTE:  Additional instances of this module (tfl2, tfl3,
# etc) should be imported to control additional devices.

# 'getData()' sets module variables for dist(distance),
# flux (signal strength) and temp(temperature in Centigrade).
# It returns a boolean value and sets a one byte error status
# code based on data values from the device.
# EXAMPLE: If flux less than 100 then dist is set to -1,
# getData() returns `False`, and status is set to "Signal weak".

# Various other commands are sent individually as necessary
# Commands are defined in the module's list of commands.
# Parameters can be entered directly (115200, 250, etc) but for
# safety, they should be chosen from the module's defined lists.

# NOTE:
#   I2C(1) is default RPi I2C port, used by real-time clock
#   Other I2C Ports are initialized in the 'boot/config.txt' file
#   I2C(0) = GPIO0 Pin 27 SDA, GPIO1 Pin 28 SCL
#   I2C(4) = GPIO8 Pin 24 SDA, GPIO9 Pin 21 SCL
#
# Press Ctrl-C to break the loop
#
# 'tmli2c' Module does not work in Windows because required
# 'smbus' module only works in Linux/Raspian/MacOS
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-'''

#  Skip a line and say 'Hello!'
print( "\n\r" + "tfli2c_test.py" +\
       "\n\r" + "14JUL2021")

import time
import sys
import tfli2c as tfl    # Import `tfli2c` module v0.0.1
from tfli2c import *    # and also import all definitions

#I2CPort = 0     # I2C(0), /dev/i2c-0, GPIO 0/1, pins 27/28
I2CPort = 4      # I2C(4), /dev/i2c-4, GPIO 8/9, pins 24/21
I2CAddr = 0x10   # Device address in Hex, Decimal 16

# - - - -  Set and Test I2C communication  - - - -
#  This function is needed to set the I2C port and
#  address values, and to test those settings.
#  • I2C(4) is the default I2C port for this host.
#  • 0x10 is the default I2C address for this device.
# - - - - - - - - - - - - - - - - - - - - - - - - -
if( tfl.begin( I2CAddr, I2CPort)):
    print( "I2C mode: ready")
else:
    print( "I2C mode: not ready")
    sys.exit()   #  quit the program if I2C bus not ready
#  - - - - - - - - - - - - - - - - - - - - - - - -'''

#  - - - - - -  Miscellaneous commands  - - - - - - -
#  These commands are for example only.
#  They are not necessary for this sketch to run.
#  There are many more commands available.
# - - - - - - - - - - - - - - - - - - - - - - - - -
#
#  - - Perform a system reset - - - - - - - -
print( "System reset: ", end = '')
tfl.softReset()
time.sleep(0.5)  # allow 500ms for reset to complete
print( "complete")
#
#  - - Get and Display the firmware version - - - - - - -
print( "Firmware version: " + tfl.getFirmwareVersion())
#
#  - - Get and display Serial Number - - - - - - -
print( "Production Code: " + tfl.getProdCode())
#
#  - -  Set and display Trigger Mode  - - - - - -
tfl.setModeTrig()
print( "Sample Mode: " + tfl.getMode())
#
#  - - -  Set and display Frame Rate  - - - - -
tfl.setFrameRate( 20)
print( "Sample Rate: " + str(tfl.getFrameRate()))
#  - - - - - - - - - - - - - - - - - - - - - - - -
#
time.sleep(0.5)     # Wait half a second.
#  - - - - - -  miscellaneous commands ends here  - - - - - - -


#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  - - - - - -  the main program loop begins here  - - - - - - -
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  Program will report an error, wait two seconds, and
#  restart up to three times; and then quit.
#
tfAttempt = 0
tfTimeLap = 0
tfTimeOld = 0
tfTimeNew = 0
#
while tfAttempt < 3:
    try:
        #  Loop until exception occurs
        while True:
            time.sleep(0.047)   # Add 47ms delay for 20Hz loop-rate
            #  Display time in milliseconds.
            tfTimeOld = tfTimeNew               #  Save new time as old
            tfTimeNew = tfl.getTime()           #  Get new time
            tfTimeLap = tfTimeNew - tfTimeOld   #  Get lap time
            print( f"Time:{tfTimeLap:{3}}ms", end = " | ")
            #  Display three main data values from the device.
            if tfl.getData():
                # Display distance in centimeters,
                print( f"Dist:{tfl.dist:{4}}cm", end= " | ")
                # display signal-strength or quality,
                print( f"Flux:{tfl.flux:{6}d}",  end= " | ")
                # and display temperature in Centigrade.
                print( f"Temp:{tfl.temp:{3}}°C",  )
            else:                  # If the command fails...
                tfl.printStatus()  # display the error status
    #
    #  Use control-C to break loop.
    except KeyboardInterrupt:
        print( 'Keyboard Interrupt')
        break
    #
    #  Catch all other exceptions.
    except:
        eType = sys.exc_info()[0]  #  Return exception type
        print( eType)
        tfAttempt += 1
        print( "Attempts: " + str(tfAttempt))
        time.sleep(2.0)     #  Wait two seconds and retry.
#
print( "That's all folks!") #  Say "Goodbye!"
sys.exit()                  #  Clean up the OS and exit.
#
# - - - - - -  the main program sequence ends here  - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
