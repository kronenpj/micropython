# Author: Kevin Köck
# Copyright Kevin Köck 2019 Released under the MIT license
# Created on 2019-03-29 

__updated__ = "2019-04-06"
__version__ = "0.1"

try:
    from pysmartnode.libraries.arduinoGPIO.arduinoGPIO import ArduinoControl
except:
    try:
        from micropython_arduino_control.arduinoGPIO import ArduinoControl
    except:
        from arduinoGPIO.arduinoControl import ArduinoControl
import time
import machine

arduino = ArduinoControl(machine.Pin(19))

errors = {}


def runTest(descr, f, *args):
    global errors
    try:
        res = f(*args)
    except Exception as e:
        if arduino.rom2str(args[0]) not in errors:  # always ROM
            errors[arduino.rom2str(args[0])] = {}
        errors[arduino.rom2str(args[0])][descr] = e
        res = "Failed"
    print(descr, res)
    return res if res != "Failed" else None


def test():
    global errors
    errors = {}
    a = bytearray(7)
    for i in range(7):
        a[i] = i * 10
    print("Test started")
    print("Roms available:", arduino.scan())
    # time.sleep(1)
    roms = arduino.scanSafely()
    print("Scan safely:", roms)
    print("--------------------------")
    for rom in roms:
        runTest("Testing rom:", arduino.rom2str, rom)
        # time.sleep(1)
        runTest("Client version:", arduino.clientVersion, rom)
        # time.sleep(1)
        dps = runTest("Digital pins:", arduino.digitalPins, rom)
        # time.sleep(1)
        aps = runTest("Analog pins:", arduino.analogPins, rom)
        # time.sleep(1)
        runTest("Sending scratchpad {!s}:".format(a), arduino.writeScratchpad, rom, a)
        # time.sleep(1)
        runTest("Reading scratchpad:", arduino.readScratchpad, rom)
        # time.sleep(1)
        for p in range(dps):
            print("---")
            if p != 2:  # onewire pin
                runTest("PinMode OUTPUT         Pin {!s}:".format(p), arduino.pinMode, rom, p, 1)
                # time.sleep(1)
                runTest("DigitalWrite 1         pin {!s}:".format(p), arduino.digitalWrite, rom, p, 1)
                if p == 13:
                    time.sleep(1)
                runTest("DigitalWrite 0         pin {!s}:".format(p), arduino.digitalWrite, rom, p, 0)
                # time.sleep(1)
                runTest("PinMode INPUT          pin {!s}:".format(p), arduino.pinMode, rom, p, 0)
                # time.sleep(1)
                runTest("DigitalRead            pin {!s}:".format(p), arduino.digitalRead, rom, p)
                # time.sleep(1)
                runTest("AnalogWrite duty 256   pin {!s}:".format(p), arduino.analogWrite, rom, p, 256)
                # time.sleep(1)
                runTest("AnalogWrite duty 0     pin {!s}:".format(p), arduino.analogWrite, rom, p, 0)
                # time.sleep(1)
        for p in range(aps):
            runTest("AnalogRead             pin A{!s}:".format(p), arduino.analogRead, rom, p)
        print("-----------------------------------------------------\n")
    print("\nTest done\n")
    if len(errors) == 0:
        print("No errors")
    else:
        print("Errors:")
        for d in errors:
            print("---------------")
            print("Rom:", d)
            print("")
            for er in errors[d]:
                print(er, "|", errors[d][er])
        print("--------------")


test()
