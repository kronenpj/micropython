# Author: Kevin Köck
# Copyright Kevin Köck 2020 Released under the MIT license
# Created on 2020-12-28 from GPIO.py

"""
example config:
{
    package: .switches.garageDoorToggle
    component: GarageDoorToggle
    constructor_args: {
        pin: D4
        active_high: true           #optional, defaults to active high
        # mqtt_topic: sometopic     #optional, topic needs to have /set at the end, defaults to <home>/<device-id>/GPIO/<pin>
        # instance_name: name       #optional, name of the gpio instance, will be generated automatically
    }
}
NOTE: additional constructor arguments are available from base classes, check COMPONENTS.md!
"""

__updated__ = "2020-12-28"
__version__ = "1.0"

import gc

import machine
import uasyncio as asyncio
from micropython import const
from pysmartnode import config
from pysmartnode.components.machine.pin import Pin
from pysmartnode.utils.component.button import ComponentButton

COMPONENT_NAME = "GarageDoorToggle"

_mqtt = config.getMQTT()
_unit_index = -1

gc.collect()

class GarageDoorToggle(ComponentButton):
    def __init__(self, pin, debounce=100, active_high=True, mqtt_topic=None, instance_name=None, **kwargs):
        mqtt_topic = mqtt_topic or _mqtt.getDeviceTopic(
            "{!s}/{!s}".format(COMPONENT_NAME, str(pin)), is_request=True)
        global _unit_index
        _unit_index += 1
        super().__init__(COMPONENT_NAME, __version__, _unit_index, mqtt_topic=mqtt_topic,
                         instance_name=instance_name or "{!s}_{!s}".format(COMPONENT_NAME, pin),
                         **kwargs)
        self.pin = Pin(pin, machine.Pin.OUT, value=0 if active_high else 1)
        self.debounce = debounce
        self._state = not active_high
        self._active_high = active_high

    async def _on(self):
        self.pin.value(1 if self._active_high else 0)
        await asyncio.sleep_ms(const(self.debounce))
        self.pin.value(0 if self._active_high else 1)
        return True

    async def _off(self):
        return True
