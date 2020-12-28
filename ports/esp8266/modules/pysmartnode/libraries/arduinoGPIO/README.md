# Micropython Arduino Control
Micropython library to control an Arduino using the 1-wire protocol.


This is a simple library to control your Arduinos pins from a micropython device using the 1-wire protocol.
Supported commands are:
- pinMode
- digitalWrite
- digitalRead
- analogWrite
- analogRead


All communication is secured with crc to prevent corruption and failed transmissions will be retransmitted by the host for a few times before raising an error.

The micropython library also provides ADC and Pin Objects compatible to the machine.ADC and machine.Pin objects so they can be used in any application.
Only word of caution: Sending a command takes ~15ms which can be too much for some applications.


# Micropython side

## Installation

Generally this library can be installed in different ways. In this Readme we will follow this:

Copy the directory [arduinoGPIO](./arduinoGPIO) onto your device's internal storage.
This can be done using [rshell](https://github.com/dhylands/rshell).

```
git clone https://github.com/kevinkk525/micropython_arduino_control
cd micropython_arduino_control
rshell -p /dev/ttyUSB0 "cp -r arduinoGPIO /pyboard"
```

## Usage ArduinoControl

The main module is [arduinoControl](./arduinoGPIO/arduinoControl.py). All features can be used with this module.
Every method will take the ROM of the device that should be controlled. 
There are no features implemented that will be executed by all devices at the same time because every command will be confirmed by the client with an answer.

```Python
from arduinoGPIO.arduinoControl import ArduinoControl
import machine
import time

arduinoControl = ArduinoControl(machine.Pin(19)) # 19: pin number of the 1-wire connection

roms=arduinoControl.scanSafely() # .scan() can be used too, this is just safer as it scans multiple times
available_digital_pins=arduinoControl.digitalPins(roms[0])
available_analog_pins=arduinoControl.analogPins(roms[0])
arduinoControl.digitalWrite(roms[0], 13, 1) # led on
time.sleep(2)
arduinoControl.digitalWrite(roms[0], 13, 0) # led off

```

## Usage Arduino Class

The arduino class is just a wrapper to remove the need to pass the ROM to each command and represents one Arduino device with a specific ROM.

```Python
from arduinoGPIO.arduinoControl import ArduinoControl
from arduinoGPIO.arduino import Arduino
import machine
import time

arduinoControl = ArduinoControl(machine.Pin(19)) # 19: pin number of the 1-wire connection
roms=arduinoControl.scanSafely() # .scan() can be used too, this is just safer as it scans multiple times

arduino = Arduino(arduinoControl, roms[0])

available_digital_pins=arduino.digitalPins()
available_analog_pins=arduino.analogPins()
arduino.digitalWrite(13, 1) # led on
time.sleep(2)
arduino.digitalWrite(13, 0) # led off
```

## Usage of Pin and ADC objects

The ArduinoControl class can create Pin and ADC objects as well as the Arduino Class. Only difference is that the Arduino Class doesn't need a ROM argument.

```Python
from arduinoGPIO.arduinoControl import ArduinoControl
from arduinoGPIO.arduino import Arduino
import machine
import time

arduinoControl = ArduinoControl(machine.Pin(19)) # 19: pin number of the 1-wire connection
roms=arduinoControl.scanSafely() # .scan() can be used too, this is just safer as it scans multiple times

arduino = Arduino(arduinoControl, roms[0])

adc=arduino.ADC(0,vcc=3.3) # Analog pin 0. optional argument vcc used for calculating voltages
print(adc.read())
print(adc.readVoltage())

led=arduinoControl.Pin(roms[0],13)
led.on()
time.sleep(1)
led.off()

```


# Arduino Side

## Requirements

Hardware:
<br>I tested this with Atmega328 modules (Arduino Uno, Arduino Pro, ...) but every device capable of running the required libraries should work.
<br>The library uses digital pin 2 for the 1-wire communication, which can be adapted in the Sketch of course.

Software:
<br>The only required external library is *OneWireHub* which can be found in the integrated Arduino IDE libraries.

## Sketch

The Arduino Sketch is located in [ProjectArduinoControl.ino](./arduino_onewire_sketch/ProjectArduinoControl/ProjectArduinoControl.ino).
<br>There you have to adapt the *UNIT_ID* to be unique in your 1-wire network for each device.

These are the first lines of the Sketch:

```cpp
#include "OneWireHub.h"
#include "Control.h"

constexpr uint8_t pin_led {13};
constexpr uint8_t pin_onewire {2};

auto hub = OneWireHub(pin_onewire);

#define UNIT_ID 0x03 //change this to be unique for every device in your 1-wire network

auto arduino = Control(Control::family_code, 0x00,0x00,0xB2,0x18,0xDA,UNIT_ID);
```

# Motivation

I was faced with the situation of having to connect 16 simple analog sensors to my ESP32 running micropython.
These were all within a few meters from the device but would require me to run a lot of cables and still use an analog multiplexer and a multiplexer for the power supply lines as these devices are not supposed to be powered all the time.
Therefore the easier solution was to have small, power efficient and cheap Arduinos do the sensor power toggling and reading.
This way I only need to run one cable with Vcc,Data and GND between all Arduinos and can reliably read all 16 sensors.