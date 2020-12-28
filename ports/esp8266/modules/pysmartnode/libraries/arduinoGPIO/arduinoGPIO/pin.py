# Author: Kevin Köck
# Copyright Kevin Köck 2019 Released under the MIT license
# Created on 2019-04-03 

__updated__ = "2019-04-03"
__version__ = "0.1"

import machine
from .arduinoControl import ArduinoControl


class Pin:
    """
    Attempt to make a compatible Pin version to machine.Pin.
    This class does not need an Arduino Object translating between the ArduinoCtonrol object.
    """
    IN = machine.Pin.IN
    OUT = machine.Pin.OUT

    def __init__(self, arduinoControl: ArduinoControl, rom: bytearray, pin: int, mode=machine.Pin.OUT, pull=None,
                 value=None, *args, **kwargs):
        self._a = arduinoControl
        self._p = pin
        self._r = rom if type(rom) == bytearray else arduinoControl.str2rom(rom)
        if arduinoControl.digitalPins(rom) < pin:
            raise AttributeError("Selected pin number higher than available pins")
        self.mode(mode)
        if value is not None:
            self._a.digitalWrite(rom, pin, value)
        # no open_drain implemented (client side, whatever value works on the arduino).
        # pullup not implemented

    def value(self, value: int = None):
        if value is None:
            return self._a.digitalRead(self._r, self._p)
        return self._a.digitalWrite(self._r, self._p, value)

    def mode(self, mode):
        self._a.pinMode(self._r, self._p, 0 if mode == machine.Pin.OUT else (1 if mode == machine.Pin.IN else mode))

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
