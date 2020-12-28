#ifndef ONEWIRE_Control_H
#define ONEWIRE_Control_H

#include "OneWireItem.h"

#define DEBUG false

enum {
    PIN_MODE = 0x10,		//!< Set pin mode
    DIGITAL_READ = 0x22,	//!< Read digital pin
    DIGITAL_WRITE = 0x32,	//!< Write digital pin
    ANALOG_READ = 0x44,		//!< Read analog pin
    ANALOG_WRITE = 0x54,	//!< Write analog pin
    DIGITAL_PINS = 0xaa,	//!< Get number of digital pins
    ANALOG_PINS = 0xbc,		//!< Get number of analog inputs
    WRITE_SCRATCHPAD = 0x4E,
    READ_SCRATCHPAD = 0xBE,
	READ_VERSION = 0xCE		//!< Read client software version
  };
//odd numbers are not working with select_rom, reason unknown

#define SUCCESS 0xEE
#define SUCCESS_CRC 0xF6


class Control : public OneWireItem
{
private:
	uint16_t client_version = 100;

    uint8_t scratchpad[9];

    void updateCRC(void);

    bool checkCRC(OneWireHub * hub, uint8_t cmd, uint8_t length);
    void sendSuccess(OneWireHub * const hub);
    void sendScratchpad(OneWireHub * const hub);

public:

    static constexpr uint8_t family_code { 0xC4 };

    Control(uint8_t ID1, uint8_t ID2, uint8_t ID3, uint8_t ID4, uint8_t ID5, uint8_t ID6, uint8_t ID7);

    void duty(OneWireHub * hub) final;

	void setValue(uint16_t value);
    uint16_t getValue() const;

};

#endif
