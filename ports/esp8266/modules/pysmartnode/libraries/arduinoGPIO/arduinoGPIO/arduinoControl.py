# Author: Kevin Köck
# Copyright Kevin Köck 2019 Released under the MIT license
# Created on 2019-03-28 

__updated__ = "2019-04-06"
__version__ = "0.2"

import onewire
from micropython import const
import utime as time
from machine import Pin

FAMILY_CODE = const(0xC4)

# COMMANS
PIN_MODE = const(0x10)
DIGITAL_READ = const(0x22)
DIGITAL_WRITE = const(0x32)
ANALOG_READ = const(0x44)
ANALOG_WRITE = const(0x54)
DIGITAL_PINS = const(0xAA)
ANALOG_PINS = const(0xBC)
WRITE_SCRATCHPAD = const(0x4E)
READ_SCRATCHPAD = const(0xBE)
READ_VERSION = const(0xCE)

# Return value
SUCCESS = const(0xEE)


class ArduinoControl(onewire.OneWire):
    def __init__(self, pin: Pin, expected_devices=None):
        """
        Class to remotely control an Arduino
        :param pin: Pin object of the onewire connection
        :param expected_devices: used to warn if devices go missing (filters non-arduino devices)
        """
        if type(expected_devices) in (int, list) or expected_devices is None:
            self._expected_devices = expected_devices
        else:
            raise TypeError("expected_devices has to be None,int or list")
        super().__init__(pin)

    def _error(self, message):  # Subclass
        print(message)

    def scan(self):
        return [rom for rom in super().scan() if rom[0] == FAMILY_CODE and self.crc8(rom) == 0]

    def scanSafely(self, iter=4, wait=10, raise_on_missing=False) -> list:
        """
        Using a single scan often resulted in not all of the devices being recognized.
        :param iter: number of scans
        :param wait: waiting time between scans
        :param raise_on_missing: raise exception if an expected device is not responding
        :return: list of roms
        """
        roms = []
        exp = self._expected_devices
        scan = self.scan
        for _ in range(iter):
            r = scan()
            if exp is not None:
                if len(r) >= (exp if type(exp) == int else len(exp)):
                    roms = r
                    break
                # not checking for added devices
            for rom in r:
                if rom not in roms:
                    roms.append(rom)
            time.sleep_ms(wait)
        if type(exp) == int and len(roms) < exp:
            self._error("Missing {!s} devices".format(exp - len(roms)))
            if raise_on_missing:
                raise Exception("Missing {!s} devices".format(exp - len(roms)))
        elif type(exp) == list and len(exp) < len(roms):
            for d in exp:
                if d not in roms:
                    self._error("Missing device {!s}".format(d))
            if raise_on_missing:
                raise Exception("Missing {!s} devices".format(len(exp) - len(roms)))
        return roms

    def _sendData(self, rom: bytearray, com, data: bytearray = None, awaiting_answer=True, length_answer=2):
        """
        Helping function for sending data and receiving the answer
        :param rom: selected device or None if only one device is connected
        :param com: command, byte
        :param data: bytearray or None
        :param awaiting_answer: bool, if answer is expected
        :param length_answer: length of expected answer
        :return: bytearray answer or True if no answer expected
        """
        a = bytearray(1)
        a[0] = com
        if data is not None:
            a.extend(data)
        crc = self.crc8(a)
        a.append(crc)
        if self.crc8(a) != 0:
            print("CRC error on generation..")
        r = bytearray(length_answer)
        for _ in range(4):
            try:
                self.reset(True)
                if rom is None:
                    self.writebyte(self.SKIP_ROM)
                else:
                    self.select_rom(rom)
                self.write(a)
                if awaiting_answer is True:
                    self.readinto(r)
            except onewire.OneWireError:
                print("OneWire error, retrying")
                time.sleep_ms(10)
                continue
            if awaiting_answer is True:
                if self.crc8(r) == 0:
                    break
                else:
                    print("CRC error, retrying")
                    time.sleep_ms(10)
            else:
                return True
        if self.crc8(r) == 0:
            # received data correctly
            if length_answer == 2 and r[0] == SUCCESS:
                return True
            return r
        else:
            raise onewire.OneWireError("Device or bus unavailable")

    def clientVersion(self, rom: bytearray) -> int:
        """
        read the version of the client firmware/code
        :param rom: selected device
        :return: int
        """
        r = self._sendData(rom, READ_VERSION, length_answer=9)
        return (r[5] << 8) | r[4]

    def readScratchpad(self, rom: bytearray) -> bytearray:
        """
        read the temporary buffer of the connect arduino. Of not much use actually.
        :param rom: selected device
        :return: bytearray
        """
        return self._sendData(rom, READ_SCRATCHPAD, None, length_answer=9)

    def writeScratchpad(self, rom: bytearray, data: bytearray) -> bool:
        """
        write to the temporary buffer of the connect arduino. Of not much use actually.
        :param rom: selected device
        :param data: bytearray to store in scratchpad
        :return: True
        """
        if len(data) != 7:
            raise AttributeError("Data has to be length 7")
        return self._sendData(rom, WRITE_SCRATCHPAD, data)

    def pinMode(self, rom: bytearray, pin: int, mode: int) -> bool:
        """
        set the pinMode of the arduino. Be careful, pinMode is the mode on the arduino, NOT the
        micropython pinMode!
        :param rom: selected device
        :param pin: pin number
        :param mode: pinMode of the arduino pin, does NOT correspond to micropython machine.Pin values
        :return: True
        """
        a = bytearray(2)
        a[0] = pin
        a[1] = mode
        return self._sendData(rom, PIN_MODE, a)

    def digitalWrite(self, rom: bytearray, pin: int, value: int) -> bool:
        """
        Set pin output to HIGH or LOW.
        :param rom: selected device
        :param pin: pin number
        :param value: 1 or 0
        :return: True
        """
        a = bytearray(3)
        a[0] = pin
        a[1] = value >> 8
        a[2] = value & 0xFF
        return self._sendData(rom, DIGITAL_WRITE, a)

    def digitalRead(self, rom: bytearray, pin: int) -> int:
        """
        Read a digital pin
        :param rom: selected device
        :param pin: pin number
        :return: int, 0 or 1
        """
        a = bytearray(1)
        a[0] = pin
        r = self._sendData(rom, DIGITAL_READ, a, length_answer=9)
        return (r[5] << 8) | r[4]

    def analogRead(self, rom: bytearray, pin: int) -> int:
        """
        Read an analog pin. Return value 0-1023
        :param rom: selected device
        :param pin: pin number
        :return:
        """
        a = bytearray(1)
        a[0] = pin
        r = self._sendData(rom, ANALOG_READ, a, length_answer=9)
        return (r[5] << 8) | r[4]

    def analogWrite(self, rom: bytearray, pin: int, duty: int) -> bool:
        """
        Write pwm mode
        :param rom: selected device
        :param pin: pin number
        :param duty: pwm duty
        :return: True
        """
        a = bytearray(3)
        a[0] = pin
        a[1] = duty >> 8
        a[2] = duty & 0xFF
        return self._sendData(rom, ANALOG_WRITE, a)

    def digitalPins(self, rom: bytearray) -> int:
        """
        Get the amount of digital pins available on the arduino device
        :param rom: selected device
        :return: int
        """
        return (self._sendData(rom, DIGITAL_PINS, length_answer=9))[3]

    def analogPins(self, rom: bytearray) -> int:
        """
        Get the amount of analog pins available on the arduino device
        :param rom: selected device
        :return: int
        """
        return (self._sendData(rom, ANALOG_PINS, length_answer=9))[3]

    def Pin(self, rom: bytearray, pin: int, *args, **kwargs):
        """
        Returns a Pin object to control one digital pin on the device matching ROM
        :param rom: slave id, bytearray or string
        :param pin: pin number
        :param args:
        :param kwargs:
        :return:
        """
        from .pin import Pin
        if type(rom) == str:
            rom = self.str2rom(rom)
        return Pin(self, rom, pin, *args, **kwargs)

    def ADC(self, rom: bytearray, pin: int, vcc: int = 5):
        from .adc import ADC
        if type(rom) == str:
            rom = self.str2rom(rom)
        return ADC(self, rom, pin, vcc)

    @staticmethod
    def rom2str(rom: bytearray) -> str:
        return ''.join('%02X' % i for i in iter(rom))

    @staticmethod
    def str2rom(rom: str) -> bytearray:
        a = bytearray(8)
        for i in range(8):
            a[i] = int(rom[i * 2:i * 2 + 2], 16)
        return a
