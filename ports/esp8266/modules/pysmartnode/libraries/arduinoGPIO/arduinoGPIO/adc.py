# Author: Kevin Köck
# Copyright Kevin Köck 2019 Released under the MIT license
# Created on 2019-04-03 

__updated__ = "2019-04-03"
__version__ = "0.1"

from .arduinoControl import ArduinoControl

try:
    from pysmartnode.components.machine.adc import pyADC
    # used to provide a unified ADC base class in my project pysmartnode.
except:
    pyADC = object


class ADC(pyADC):
    def __init__(self, arduinoControl: ArduinoControl, rom: bytearray, pin, vcc=5):
        """
        machine.ADC compatible object that can be used in any application/library.
        This class does not need an Arduino object translating between the ArduinoControl object.
        :param arduinoControl: ArduinoControl object
        :param rom: onewire slave id, can be str as it will be converted
        :param pin: pin number
        :param vcc: Voltage the arduino is running at to calculate adc voltage
        """
        super().__init__()
        self._p = pin
        self._v = vcc
        self._a = arduinoControl
        self._r = rom if type(rom) == bytearray else arduinoControl.str2rom(rom)
        if arduinoControl.analogPins(rom) < pin:
            raise AttributeError("Selected pin number higher than available pins")

    def __str__(self):
        return "ArduinoControlADC({!s},{!s})".format(self._a.rom2str(self._r), self._p)

    def readVoltage(self):
        return self.read() / 1023 * self._v

    def maxVoltage(self):
        return self._v  # arduino operating voltage

    def read(self):
        return self._a.analogRead(self._r, self._p)

    def atten(self, *args):
        raise NotImplementedError("Arduino ADC doesn't support atten")

    def width(self, *args, **kwargs):
        raise NotImplementedError("Arduino ADC doesn't support width")
