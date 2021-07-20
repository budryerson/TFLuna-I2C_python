# tfli2c
### A python module for the Benewake TFLuna LiDAR distance sensor in I2C mode

In I2C communication mode, the **TFLuna** is unique among the Benewake family of LiDAR products.  First, the selection of communications mode (UART/I2C) is made by the voltage level of Pin #5 rather than by a command. Second, the internal registers of the device can be addressed directly. And third, Benewake advises that sampling data continuously without using the Pin #6 "data ready" signal is unreliable.  For that last reason, this module switches the device from Continuous to Trigger Mode during initialization, and then sends a Trigger command before every call to read data.  The use of Trigger Mode also reduces power consumption significantly, by almost an order of magnitude.

In I2C communication mode, therefore, the **TFLuna** and the `tfli2c` library are *not compatible* with any other Benewake LiDAR device.  In serial (UART) mode, however, the **TFLuna** is highly compatible with the **TFMini-Plus** and the **TFMini-S** and they can all use the same `tfmplus` module for python projects.

This module requires and will automatically try to install the python `smbus` module.  The `smbus` and `smbus2` modules do not work and will not install in a Windows environment.

Multiple devices can be supported by importing additional instances of the module using different local names.
<hr />

### Primary Functions

`begin( addr, port)` sends I2C address and port parameters, tests communication, switches the device from its default Continuous Mode to the One-Shot or Trigger Mode, and returns a boolean result.
 
`getData()` reads the first six registers of the device and sets the value of three variables:
<br />&nbsp;&nbsp;&#8211;&nbsp; `dist` Distance to target in centimeters. Range: 0 to 1200
<br />&nbsp;&nbsp;&#8211;&nbsp; `flux` Strength or quality of return signal or error. Range: -1 and 0 to 32767
<br />&nbsp;&nbsp;&#8211;&nbsp; `temp` Temperature in quarter degrees of Celsius. Range: -25.00°C to 125.00°C<br />
  The function returns a boolean value and sets a one byte `status` code based on various data values from the device.<br />
  EXAMPLE: If ```flux < 100``` then device sets  ```dist = -1``` and the function sets ```status = TFL_WEAK``` and returns ```False```.<br />
  The function ```printStatus()```, if called, will display ```"Signal weak"```.

A variety of other commands are explicitly defined and  may be sent individually and as necessary.  They are broadly separated into "set" commands that modify device register values and and "get" commands that examine register values.
<hr />

### Explicit commands:
<br />&#8211;&nbsp;&nbsp; `saveSettings()` - save register changes
<br />&#8211;&nbsp;&nbsp; `softReset()` - reset, reboot and restart
<br />&#8211;&nbsp;&nbsp; `hardReset()` - restore factory defaults
<br />&#8211;&nbsp;&nbsp; `setI2Caddr( addrNew)` - send value of new I2C address: `0x08` to `0x77`
<br />&#8211;&nbsp;&nbsp; `setEnable()` - turn ON device light source
<br />&#8211;&nbsp;&nbsp; `setDisable()` - turn OFF device light source
<br />&#8211;&nbsp;&nbsp; `setModeCont()` - set device to sample continuously at Frame Rate
<br />&#8211;&nbsp;&nbsp; `setModeTrig()` - set device to sample only when triggered
<br />&#8211;&nbsp;&nbsp; `getMode()` - returns string of mode type: 'continuous' or 'trigger'
<br />&#8211;&nbsp;&nbsp; `setTrigger()` - trigger device to sample one time
<br />&#8211;&nbsp;&nbsp; `setFrameRate( fps)` - set device Frame Rate in frames per second: `1`to `250`
<br />&#8211;&nbsp;&nbsp; `getFrameRate()` - return two-byte unsigned word of Frame-Rate in frames per second
<br />&#8211;&nbsp;&nbsp; `getTime()` - return two-byte unsigned word of device clock in milliseconds
<br />&#8211;&nbsp;&nbsp; `getProdCode()` - return 14 character string of product serial number
<br />&#8211;&nbsp;&nbsp; `getFirmwareVersion()`  - return string of version number

<hr>

In **I2C** mode, the TFMini-Plus functions as an I2C slave device.  The default address is `0x10` (16 decimal), but is user-programmable by sending the `setI2Caddr( addrNew)` command and a parameter in the range of `0x08` to `0x77` (8 to 119).  The new address requires a `softReset()` command to take effect.  A `hardReset()` command (Restore Factory Settings) will reset the device to the default address of `0x10`.

Some commands that modify internal parameters are processed within 1 millisecond.  But other commands that require the MCU to communicate with other chips may take several milliseconds.  And some commands that erase the flash memory of the MCU, such as `saveSettings()` and `hardReset()`, may take several hundred milliseconds.

Frame Rate and most other register changes should be followed by a `saveSettings()` command, or the values may be lost when power is removed.  With the TFLuna, commands are available to examine the value of various device parameters such as internal Time, Frame Rate, Trigger Mode, Error, Version Number and Production Code.

<hr>

Also included in the package are:
<br />&nbsp;&nbsp;&#9679;&nbsp; In the `tests` folder: An example Python sketch, `tfli2c_test.py`, and a simplified version of the same code, `tfli2c_simple.py`.
<br />&nbsp;&nbsp;&#9679;&nbsp; In the `docs` folder: A recent copy of the manufacturer's Product Manual.

All of the code for this Library is richly commented to assist with understanding and in problem solving.
