#include "OneWireHub.h"
#include "Control.h"

constexpr uint8_t pin_led {13};
constexpr uint8_t pin_onewire {2};

auto hub = OneWireHub(pin_onewire);

#define UNIT_ID 0x03 //change this to be unique for every device in your 1-wire network

auto arduino = Control(Control::family_code, 0x00,0x00,0xB2,0x18,0xDA,UNIT_ID);


void setup() {
  // put your setup code here, to run once:

    Serial.begin(115200);
#if DEBUG
    Serial.println("OneWire-Hub DS18");
#endif
    Serial.flush();


    pinMode(pin_led, OUTPUT);

    // Setup OneWire
    hub.attach(arduino);
    //hub.attach(ds182);
}

void loop() {
    // following function must be called periodically
    hub.poll();
    // this part is just for debugging (USE_SERIAL_DEBUG in OneWire.h must be enabled for output)
    if (hub.hasError()) hub.printError();

}

