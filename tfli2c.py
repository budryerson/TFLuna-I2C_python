'''=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
 # Package: tfli2c
 # Developer: Bud Ryerson
 # Inception: 10 JUL 2021
 # Version:   0.0.1
 # Described: Arduino Library for the Benewake TF-Luna Lidar sensor
 #            configured for the I2C interface
 #
 # Default settings for the TF-Luna are:
 #    0x10  -  slave device address
 #    100Hz  - data frame-rate
 #
 #  There is one important function:
 #  getData( addr)
 #  send I2C address, read first six registers of device
 #  and give value to three variables
      addr : address of slave device
      dist : distance measured by the device, in cm
      flux : signal strength, quality or confidence
             If flux value too low, an error will occur.
      temp : temperature of the chip in 0.01 degrees C

      Returns true, if no error occurred.
      If false, error is defined by a status code,
      which can be displayed using `printStatus()` function.
 #
 #  There are several explicit commands. In general,
 #  the `set` commmands require a follow-on `saveSettings`
 #  and `softReset` commands.
 #
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-'''

import time
from smbus import SMBus

status = 0            # error status code
dist =   0            # distance to target
flux =   0            # signal quality or intensity
temp =   0            # internal chip temperature

# Timeout Limits for various functions
TFL_MAX_READS           = 20   # readData() sets SERIAL error
MAX_BYTES_BEFORE_HEADER = 20   # getData() sets HEADER error
MAX_ATTEMPTS_TO_MEASURE = 20

tflAddr = 0x10        # TFLuna I2C device address
                      # Range: 0x08 to 0x77
tflPort = 4           # Raspberry Pi I2C port number
                      # 4 = /dev/i2c-4, GPIO 8/9, pins 24/21

def begin( addr, port):
    global tflPort, tflAddr
    tflAddr = addr    # re-assign device address
    tflPort = port    # re-assign port number
    try:
        bus = SMBus( tflPort)
        bus.open( tflPort)
        bus.write_quick( tflAddr)
        bus.close()
        return True
    except Exception:
        return False

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#      Definitions
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# - - -  Register Names, Hex Address Numbers  - - -
# - - -  and whether Read, Write or both R/W  - - -
TFL_DIST_LO        = 0x00  # R centimeters
TFL_DIST_HI        = 0x01  # R
TFL_FLUX_LO        = 0x02  # R arbitray units
TFL_FLUX_HI        = 0x03  # R
TFL_TEMP_LO        = 0x04  # R degrees Celsius
TFL_TEMP_HI        = 0x05  # R
TFL_TICK_LO        = 0x06  # R milliseconds
TFL_TICK_HI        = 0x07  # R
TFL_ERR_LO         = 0x08  # R
TFL_ERR_HI         = 0x09  # R
TFL_VER_REV        = 0x0A  # R revision
TFL_VER_MIN        = 0x0B  # R minor release
TFL_VER_MAJ        = 0x0C  # R major release

TFL_PROD_CODE      = 0x10  # R - 14 byte serial number

TFL_SAVE_SETTINGS  = 0x20  # W -- Write 0x01 to save
TFL_SOFT_RESET     = 0x21  # W -- Write 0x02 to reboot.
                     # Lidar not accessible during few seconds,
                     # then register value resets automatically
TFL_SET_I2C_ADDR   = 0x22  # W/R -- Range 0x08,0x77.
                     # Must save and reboot to take effect.
TFL_SET_MODE       = 0x23  # W/R -- 0-continuous, 1-trigger
TFL_TRIGGER        = 0x24  # W  --  1-trigger once
TFL_DISABLE        = 0x25  # W/R -- 0-enable, 1-disable
TFL_FPS_LO         = 0x26  # W/R -- lo byte
TFL_FPS_HI         = 0x27  # W/R -- hi byte
TFL_SET_LO_PWR     = 0x28  # W/R -- 0-normal, 1-low power
TFL_HARD_RESET     = 0x29  # W  --  1-restore factory settings



# - -   Error Status Condition definitions - -
TFL_READY         =  0  # no error
TFL_SERIAL        =  1  # serial timeout
TFL_HEADER        =  2  # no header found
TFL_CHECKSUM      =  3  # checksum doesn't match
TFL_TIMEOUT       =  4  # I2C timeout
TFL_PASS          =  5  # reply from some system commands
TFL_FAIL          =  6  #           "
TFL_I2CREAD       =  7
TFL_I2CWRITE      =  8
TFL_I2CLENGTH     =  9
TFL_WEAK          = 10  # Signal Strength ≤ 100
TFL_STRONG        = 11  # Signal Strength saturation
TFL_FLOOD         = 12  # Ambient Light saturation
TFL_MEASURE       = 13
TFL_INVALID       = 14  # Invalid operation sent to sendCommand()


# - - - - - - - - - - - - - - - - - - - - - - - - - -
#             GET DATA FROM THE DEVICE
# - - - - - - - - - - - - - - - - - - - - - - - - - -
#  Return `True`/`False` whether data received without
#  error and set system status
def getData():
    ''' Get get three data values '''

    #  1. Make data and status variables global
    global status, dist, flux, temp

    #  2. Get data from the device.
    #  Open I2C communication
    bus = SMBus( tflPort)
    #  Read the first six registers
    frame = bus.read_i2c_block_data( tflAddr, 0, 6)
    #  Close I2C communication
    bus.close()

    #  3. Shift data from read array into the three variables
    dist = frame[ 0] + ( frame[ 1] << 8)
    flux = frame[ 2] + ( frame[ 3] << 8)
    temp = frame[ 4] + ( frame[ 5] << 8)
    # Convert temp to degrees from hundredths
    temp = ( temp / 100)
    # Convert Celsius to Fahrenheit
    #temp = ( temp * 9 / 5) + 32

    #  4.  Evaluate Abnormal Data Values
    if( flux < 100):           # Signal strength < 100
        status = TFL_WEAK
        return False
    elif( flux > 0x8000):      # Ambient light too strong
        status = TFL_STRONG
        return False
    elif( flux == 0xFFFF):     # Signal saturation
        status = TFL_STRONG
        return False

    #  5. Set Ready status and go home
    status = TFL_READY
    return True
#
# - - - -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - - -
#              EXPLICIT COMMANDS
# - - - - - - - - - - - - - - - - - - - - - - - - - -
#  - - - - -    SAVE SETTINGS   - - - - -
def saveSettings():
    bus = SMBus( tflPort)
    bus.write_byte_data( tflAddr, TFL_SAVE_SETTINGS, 1)
    bus.close()

#  - - - -   SOFT RESET aka Reboot  - - - -
def softReset():
    bus = SMBus( tflPort)
    bus.write_byte_data( tflAddr, TFL_SOFT_RESET, 2)
    bus.close()

#  - - - -   HARD RESET to Factory Defaults  - - - -
def hardReset():
    bus = SMBus( tflPort)
    bus.write_byte_data( tflAddr, TFL_HARD_RESET, 1)
    bus.close()

#  - - - - - -    SET I2C ADDRESS   - - - - - -
#  Range: 0x08, 0x77.  Must be followed by
#  `saveSettings()` and 'softReset()` commands
def setI2Caddr():
    bus = SMBus( tflPort)
    bus.write_byte_data( tflAddr, TFL_SET_I2C_ADDR, addrNew)
    bus.close()

#  - - - - -   SET ENABLE   - - - - -
#  Turn on LiDAR
#  Must be followed by Save and Reset commands
def setEnable():
    bus = SMBus( tflPort)
    bus.write_byte_data( tflAddr, TFL_DISABLE, 0)
    bus.close()

#  - - - - -   SET DISABLE   - - - - -
#  Turn off LiDAR
#  Must be followed by Save and Reset commands
def setDisable():
    bus = SMBus( tflPort)
    bus.write_byte_data( tflAddr, TFL_DISABLE, 1)
    bus.close()

#  - - - - - -   SET CONTINUOUS MODE   - - - - - -
#  Continuous ranging mode
#  Must be followed by Save and Reset commands
def setModeCont():
    bus = SMBus( tflPort)
    bus.write_byte_data( tflAddr, TFL_SET_MODE, 0)
    bus.close()

#  - - - - - -   SET TRIGGER MODE   - - - - - -
#  Sample range only once when triggered
#  Must be followed by Save and Reset commands
def setModeTrig():
    bus = SMBus( tflPort)
    bus.write_byte_data( tflAddr, TFL_SET_MODE, 1)
    bus.close()

def getMode():
    bus = SMBus( tflPort)
    mode = bus.read_byte_data( tflAddr, TFL_SET_MODE)
    bus.close()
    if mode == 0: return 'continuous'
    else:         return 'trigger'

#  - - - - - -   SET TRIGGER   - - - - - =
# Trigger device to sample one time
def setTrigger():
    bus = SMBus( tflPort)
    bus.write_byte_data( tflAddr, TFL_TRIGGER, 1)
    bus.close()

#  - - - - -    SET FRAME RATE   - - - - - -
#  Write `fps` (frames per second) to device
#  Command must be followed by `saveSettings()`
#  and `softReset()` commands.
def setFrameRate( fps):
    bus = SMBus( tflPort)
    bus.write_word_data( tflAddr, TFL_FPS_LO, ( fps))
    bus.close()

#  - - - - -    GET FRAME RATE   - - - - - -
#  Returns Frame Rate value as an integer
def getFrameRate():
    bus = SMBus( tflPort)
    fps = bus.read_word_data( tflAddr, TFL_FPS_LO)
    bus.close()
    return fps

#  - - - -  GET DEVICE TIME (in milliseconds) - - -
#  Returns milliseconds since power on as an integer
def getTime():
    bus = SMBus( tflPort)           #  Open I2C communication
    tim = bus.read_word_data( tflAddr, TFL_TICK_LO)     #  Get bytes of time
    #tim = bus.read_byte_data( tflAddr, TFL_TICK_HI)
    bus.close()                  #  Close I2C communication
    #return (timHi << 8) + timLo  # return time as a 16 bit integer
    return tim

#  - -  GET PRODUCTION CODE (Serial Number) - - -
def getProdCode():
    prodcode = ''
    bus = SMBus( tflPort)   #  Open I2C communication
    for i in range( 14):    #  Build the 'production code' string
        prodcode += chr(bus.read_byte_data( tflAddr, TFL_PROD_CODE + i))
    bus.close()             #  Close I2C communication
    return prodcode

#  - - - -    GET FIRMWARE VERSION   - - - -
def getFirmwareVersion():
    version = ''
    bus = SMBus( tflPort)      #  Open I2C communication
    #  Build the 'version' string
    version =\
        str( bus.read_byte_data( tflAddr, TFL_VER_MAJ)) + '.' +\
        str( bus.read_byte_data( tflAddr, TFL_VER_MIN)) + '.' +\
        str( bus.read_byte_data( tflAddr, TFL_VER_REV))
    bus.close()             #  Close I2C communication
    return version          #  Return the version string

# - - - - - - - - - - - - - - - - - - - - -


#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  - - - - -    The following are for testing purposes   - - - -
#     They interpret error status codes and display HEX data
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
#  Called by either 'printFrame()' or 'printReply()'
#  Print status condition either 'READY' or error type
def printStatus():
    ''' Print status condition'''
    global status

    print("Status: ", end= '')
    if( status == TFMP_READY):       print( "READY", end= '')
    elif( status == TFMP_SERIAL):    print( "SERIAL", end= '')
    elif( status == TFMP_HEADER):    print( "HEADER", end= '')
    elif( status == TFMP_CHECKSUM):  print( "CHECKSUM", end= '')
    elif( status == TFMP_TIMEOUT):   print( "TIMEOUT", end= '')
    elif( status == TFMP_PASS):      print( "PASS", end= '')
    elif( status == TFMP_FAIL):      print( "FAIL", end= '')
    elif( status == TFMP_I2CREAD):   print( "I2C-READ", end= '')
    elif( status == TFMP_I2CWRITE):  print( "I2C-WRITE", end= '')
    elif( status == TFMP_I2CLENGTH): print( "I2C-LENGTH", end= '')
    elif( status == TFMP_WEAK):      print( "Signal weak", end= '')
    elif( status == TFMP_STRONG):    print( "Signal saturation", end= '')
    elif( status == TFMP_FLOOD):     print( "Ambient light saturation", end= '')
    else:                            print( "OTHER", end= '')
    print()


#  - - - -   For test and troubleshooting:   - - - -
#  - - - -   Format a value as hexadecimal   - - - -
'''
for i in range( len(cmndData)):
    print( f" {cmndData[i]:0{2}X}", end='')
print()
'''
# f"{value:#0{padding}X}"
# formats 'value' as a hex number padded with
# 0s to the length of 'padding'
#  - - - - - - - - - - - - - - - - - - - - - - - - -

#  Frame Rates apply to all instances of the library
# - - - -  FPS (Low Power Mode) - - - -
FPS_1            = 0x0001
FPS_2            = 0x0002
FPS_3            = 0x0003
FPS_4            = 0x0004
FPS_5            = 0x0005
FPS_6            = 0x0006
FPS_7            = 0x0007
FPS_8            = 0x0008
FPS_9            = 0x0009
FPS_10           = 0x000A

# - - - -  FPS (High Power Mode) - - - -
FPS_20           = 0x0014
FPS_35           = 0x0023
FPS_71           = 0x0047  # 7
FPS_83           = 0x0053  # 6
FPS_100          = 0x0064  # 5
FPS_125          = 0x007D  # 4
FPS_166          = 0x00A6  # 3
FPS_250          = 0x00FA  # 2

#  Frame Rate definitions need to be exported
__all__ = ['FPS_1', 'FPS_2', 'FPS_3', 'FPS_4', 'FPS_5', 'FPS_6',
           'FPS_7', 'FPS_8', 'FPS_9', 'FPS_10', 'FPS_20', 'FPS_35',
           'FPS_71', 'FPS_83', 'FPS_100', 'FPS_125', 'FPS_166', 'FPS_250']

# If this module is executed by itself
if __name__ == "__main__":
    print( "tfli2c - This Python module supports the Benewake" +\
           " TFLuna Lidar device in I2C mode.")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
