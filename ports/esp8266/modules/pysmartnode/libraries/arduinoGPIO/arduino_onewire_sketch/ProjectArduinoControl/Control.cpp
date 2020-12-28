#include "Control.h"
  
Control::Control(uint8_t ID1, uint8_t ID2, uint8_t ID3, uint8_t ID4, uint8_t ID5, uint8_t ID6, uint8_t ID7) : OneWireItem(ID1, ID2, ID3, ID4, ID5, ID6, ID7)
{

}

void Control::updateCRC()
{
    scratchpad[8] = crc8(scratchpad, 8);
}

bool Control::checkCRC(OneWireHub * const hub, uint8_t cmd, uint8_t length)
{
    uint8_t crc;
    hub->recv(&scratchpad[1],length+1);
    scratchpad[0]=cmd;
    crc=crc8(scratchpad,length+2);
    if (crc!=0)
    {
        #if DEBUG
        Serial.print("CRC mistmatch command ");Serial.println(cmd);
        #endif
        return false;
    }
    return true;
}

void Control::sendSuccess(OneWireHub * const hub)
{
    hub->send(SUCCESS);
    hub->send(SUCCESS_CRC);
}

void Control::sendScratchpad(OneWireHub * const hub)
{
	updateCRC();
	hub->send(scratchpad,9);
}

void Control::duty(OneWireHub * const hub)
{
    uint8_t cmd;
	uint16_t value;
	uint8_t pin;
	uint8_t mode;
      
    if (hub->recv(&cmd,1)) return;

    switch (cmd)
    {
        case WRITE_SCRATCHPAD: // WRITE SCRATCHPAD
            // write 7 bytes of data to scratchpad[1:7] + crc
            if (checkCRC(hub, cmd,7)==false) break;
            sendSuccess(hub);
            #if DEBUG
            Serial.println("Wrote scratchpad");
            #endif
            break;

        case READ_SCRATCHPAD: // READ SCRATCHPAD
            if (checkCRC(hub, cmd,0)==false) break;
            sendScratchpad(hub);
            break;

		case PIN_MODE:
		    if (checkCRC(hub, cmd,2)==false) break;
        	pin=scratchpad[1];
        	mode=scratchpad[2];
        	pinMode(pin,mode);
        	sendSuccess(hub);
			#if DEBUG
        	Serial.print("pin:");Serial.println(pin);
        	Serial.print("mode:");Serial.println(mode);
        	#endif
            break;

        case DIGITAL_READ:
        	if (checkCRC(hub, cmd,1)==false) break;
			pin=scratchpad[1];
			value=digitalRead(pin);
			setValue(value);
			sendScratchpad(hub);
        	break;

        case DIGITAL_WRITE:
            if (checkCRC(hub, cmd,3)==false) break;
        	pin=scratchpad[1];
        	value=((scratchpad[2]<<8)|scratchpad[3]);
        	digitalWrite(pin,value);
        	sendSuccess(hub);
        	#if DEBUG
        	Serial.print("pin:");Serial.println(pin);
			Serial.print("value:");Serial.println(value);
			#endif
        	break;

        case ANALOG_READ:
        	if (checkCRC(hub, cmd,1)==false) break;
        	pin=scratchpad[1];
        	value=analogRead(pin);
        	setValue(value);
        	sendScratchpad(hub);
			#if DEBUG
        	Serial.print("pin:");Serial.println(pin);
			Serial.print("read value:");Serial.println(value);
			#endif
        	break;

        case ANALOG_WRITE:
        	if (checkCRC(hub, cmd,3)==false) break;
			pin=scratchpad[1];
			value=((scratchpad[2]<<8)|scratchpad[3]);
			analogWrite(pin,value);
            sendSuccess(hub);
			#if DEBUG
			Serial.print("pin:");Serial.println(pin);
			Serial.print("analogWrite value:");Serial.println(value);
			#endif
			break;

        case DIGITAL_PINS:
        	if (checkCRC(hub, cmd,0)==false) break;
        	scratchpad[3]=NUM_DIGITAL_PINS;
        	sendScratchpad(hub);
        	break;

        case ANALOG_PINS:
        	if (checkCRC(hub, cmd,0)==false) break;
			scratchpad[3]=NUM_ANALOG_INPUTS;
			sendScratchpad(hub);
			break;

        case READ_VERSION:
        	if (checkCRC(hub, cmd,0)==false) break;
        	setValue(client_version);
        	sendScratchpad(hub);
        	break;

        default:
            hub->raiseSlaveError(cmd);

        //TODO: add error code response on crc mismatch or unknown command
		#if DEBUG
		Serial.print("COM:");Serial.println(cmd);
		#endif
    }
}


void Control::setValue(const uint16_t value)
{
	scratchpad[4] = (value&0xFF);
	scratchpad[5] = (value>>8);
}

uint16_t Control::getValue(void) const
{
	return static_cast<uint16_t>((scratchpad[5]<<8)|scratchpad[4]);
}
