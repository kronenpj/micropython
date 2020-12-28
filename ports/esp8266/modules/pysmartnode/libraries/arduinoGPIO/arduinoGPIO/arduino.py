# Author: Kevin Köck
# Copyright Kevin Köck 2019 Released under the MIT license
# Created on 2019-04-03 

__updated__ = "2019-04-06"
__version__ = "0.1"

from .arduinoControl import ArduinoControl

try:
    from pysmartnode.components.machine.adc import pyADC
except:
    pyADC = object
import machine


class Arduino:
    def __init__(self, arduinoControl: ArduinoControl, rom: bytearray):
        self._c = arduinoControl
        self._r = rom
        self._dp = arduinoControl.digitalPins(rom)
        self._ap = arduinoControl.analogPins(rom)

    def __str__(self):
        return "Arduino({!s})".format(self._c.rom2str(self._r))

    def _checkDpin(self, pin: int):
        if pin > self._dp:
            raise AttributeError("Selected pin number higher than available pins")

    def _checkApin(self, pin: int):
        if pin > self._ap:
            raise AttributeError("Selected pin number higher than available pins")

    def clientVersion(self):
        return self._c.clientVersion(self._r)

    def pinMode(self, pin: int, mode: int) -> bool:
        self._checkDpin(pin)
        return self._c.pinMode(self._r, pin, mode)

    def digitalWrite(self, pin: int, value: int) -> bool:
        self._checkDpin(pin)
        return self._c.digitalWrite(self._r, pin, value)

    def digitalRead(self, pin: int) -> int:
        self._checkDpin(pin)
        return self._c.digitalRead(self._r, pin)

    def analogRead(self, pin: int) -> int:
        self._checkApin(pin)
        return self._c.analogRead(self._r, pin)

    def analogWrite(self, pin: int, duty: int) -> bool:
        self._checkDpin(pin)
        return self._c.analogWrite(self._r, pin, duty)

    def digitalPins(self) -> int:
        return self._dp

    def analogPins(self) -> int:
        return self._ap

    def Pin(self, pin, *args, **kwargs):
        return Pin(self, pin, *args, **kwargs)

    def ADC(self, pin, vcc=5):
        return ADC(self, pin, vcc)


class Pin:
    """
    Attempt to make a compatible Pin version to machine.Pin
    """
    IN = machine.Pin.IN
    OUT = machine.Pin.OUT

    def __init__(self, arduino: Arduino, pin: int, mode=machine.Pin.OUT, pull=None, value=None, *args, **kwargs):
        self._a = arduino
        self._p = pin
        self.mode(mode)
        if value is not None:
            self._a.digitalWrite(pin, value)
        # no open_drain implemented (but on the client side the passed value will be used).
        # pullup not implemented

    def value(self, value: int = None):
        if value is None:
            return self._a.digitalRead(self._p)
        return self._a.digitalWrite(self._p, value)

    def mode(self, mode):
        self._a.pinMode(self._p, 0 if mode == machine.Pin.OUT else (1 if mode == machine.Pin.IN else mode))

    def __call__(self, value=None):
        return self.value(value)

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def pull(self, *args, **kwargs):
        raise NotImplementedError

    def drive(self, *args, **kwargs):
        raise NotImplementedError

    def irq(self, *args, **kwargs):
        raise NotImplementedError


class ADC(pyADC):
    def __init__(self, arduino: Arduino, pin, vcc=5):
        """
        machine.ADC compatible object that can be used in any application/library
        :param arduino: Arduino object the pin belongs to
        :param pin: pin number
        :param vcc: Voltage the arduino is running at to calculate adc voltage
        """
        super().__init__()
        self._p = pin
        self._v = vcc
        self._a = arduino

    def __str__(self):
        return "ArduinoADC({!s})".format(self._p)

    def maxVoltage(self):
        return self._v  # arduino operating voltage

    def readVoltage(self):
        return self.read() / 1023 * self._v

    def read(self):
        return self._a.analogRead(self._p)

    def atten(self, *args):
        raise NotImplementedError("Arduino ADC doesn't support atten")

    def width(self, *args, **kwargs):
        raise NotImplementedError("Arduino ADC doesn't support width")
