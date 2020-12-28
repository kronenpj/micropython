from machine import I2C, Pin
import uasyncio as asyncio


class HTU21D(object):
    ADDRESS = 0x40
    ISSUE_TEMP_ADDRESS = 0xE3
    ISSUE_HU_ADDRESS = 0xE5

    def __init__(self, scl=None, sda=None, i2c=None):
        """Initiate the HUT21D

        Args:
            scl (int): Pin id where the sdl pin is connected to
            sda (int): Pin id where the sda pin is connected to
        """
        if i2c is not None:
            self.i2c = i2c
        else:
            self.i2c = I2C(scl=Pin(scl), sda=Pin(sda), freq=100000)
        self.running = False

    def _crc_check(self, value):
        """CRC check data

        Notes:
            stolen from https://github.com/sparkfun/HTU21D_Breakout

        Args:
            value (bytearray): data to be checked for validity

        Returns:
            True if valid, False otherwise
        """
        remainder = ((value[0] << 8) + value[1]) << 8
        remainder |= value[2]
        divsor = 0x988000

        for i in range(0, 16):
            if remainder & 1 << (23 - i):
                remainder ^= divsor
            divsor >>= 1

        if remainder == 0:
            return True
        else:
            return False

    async def _issue_measurement_async(self, write_address):
        """Issue a measurement.

        Args:
            write_address (int): address to write to
        :return:
        """
        while self.running:
            await asyncio.sleep_ms(160)
        self.running = True
        try:
            # self.i2c.start()
            self.i2c.writeto_mem(int(self.ADDRESS), int(write_address), '')
            # self.i2c.stop()
            data = bytearray(3)
        except Exception as e:
            print(e)
            self.running = False
            return None
        await asyncio.sleep_ms(50)
        try:
            self.i2c.readfrom_into(self.ADDRESS, data)
            if not self._crc_check(data):
                raise ValueError()
            raw = (data[0] << 8) + data[1]
            raw &= 0xFFFC
            self.running = False
            return raw
        except Exception as e:
            print(e)
            self.running = False
            return None

    async def temperature_async(self):
        """Calculate temperature"""
        raw = await self._issue_measurement_async(self.ISSUE_TEMP_ADDRESS)
        # TODO: check why raw is sometimes 0
        if raw is None:  # or raw == 0:
            return None
        return -46.85 + (175.72 * raw / 65536)

    async def humidity_async(self):
        """Calculate humidity"""
        raw = await self._issue_measurement_async(self.ISSUE_HU_ADDRESS)
        if raw is None:  # or raw == 0:
            return None
        return -6 + (125.0 * raw / 65536)
