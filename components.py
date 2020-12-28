from pysmartnode import config
import gc

#gc.collect()
#from pysmartnode.components.machine.i2c import I2C

#gc.collect()  # It's important to call gc.collect() to keep the RAM fragmentation to a minimum
#from pysmartnode.components.sensors.htu21d import HTU21D

# gc.collect()
# from pysmartnode.components.machine.button import Button

gc.collect()
from pysmartnode.components.sensors.garageDoorSensor import GarageDoorSensor

gc.collect()
from pysmartnode.components.switches.garageDoorToggle import GarageDoorToggle

#gc.collect()
#from pysmartnode.components.machine.easyGPIO import GPIO

#gc.collect()
#i2c = I2C(SCL="D6", SDA="D5")
#config.addComponent("i2c", i2c)

#gc.collect()
#htu = HTU21D(i2c, precision_temp=2, precision_humid=1, temp_offset=-2.0, humid_offset=10.0)
#config.addComponent("htu", htu)

# gc.collect()
# button = Button(pin="D2")
# config.addComponent("button", button)

gc.collect()
button = GarageDoorToggle(pin="D2", debounce=150, active_high=True)
config.addComponent("garagetoggle1", button)

gc.collect()
garage1 = GarageDoorSensor(sense_pin="D1", interval_reading=10)
config.addComponent("garage1", garage1)

#gc.collect()
#sensor = GPIO(discover_pins=["D4", "D5"])
#config.addComponent("gpio", gpio)  # This is optional, it just puts
# your component in the dictionary where all registered components are.
