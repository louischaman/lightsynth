#include <array>

#include <MIDI.h>
#include <Bounce.h>
#include "actuators.h"

// Setup USB MIDI if available.
#if defined(USBCON)
#include <midi_UsbTransport.h>

static const unsigned sUsbTransportBufferSize = 16;
typedef midi::UsbTransport<sUsbTransportBufferSize> UsbTransport;

UsbTransport sUsbTransport;

MIDI_CREATE_INSTANCE(UsbTransport, sUsbTransport, MIDI);

#else // No USB available, fallback to Serial
MIDI_CREATE_DEFAULT_INSTANCE();
#endif


// Default midi channel.
static constexpr auto channel {1};
// Button bounce time.
static constexpr auto bounceTime {5};


//// Inputs

// Selector - Choose between 6 voices
// range of values [0:5[
constexpr auto selectorSwitchPositions {6};
const std::array<Bounce, selectorSwitchPositions> selectorSwitch {
    Bounce(4, bounceTime),
    Bounce(5, bounceTime),
    Bounce(6, bounceTime),
    Bounce(7, bounceTime),
    Bounce(8, bounceTime),
    Bounce(9, bounceTime),
};
MidiSwitch<selectorSwitchPositions> selector(channel, 0, selectorSwitch);

// Auto Play button
MidiButton autoPlay(channel, 1, 10, bounceTime);

// // Arp on/off
MidiButton arpOnOff(channel, 2, 11, bounceTime);
// Bounce arpOnOffButton(, bounceTime);

// // Scale on/off
MidiButton scaleOnOff(channel, 3, 12, bounceTime);
// Bounce scaleOnOffButton(, bounceTime);

// Sustain on/half/off
constexpr auto sustainAmountPositions {2};
const std::array<Bounce, sustainAmountPositions> sustainAmount {
    Bounce(13, bounceTime),
    Bounce(14, bounceTime),
};
MidiSwitch<sustainAmountPositions> sustain(channel, 4, sustainAmount);

// FX on/off
MidiButton fxOnOff(channel, 5, 15, bounceTime);



// Arp rate pot
MidiPot<decltype(usbMIDI), usbMIDI> arpRate(channel, 6, 9);

// // Onset pot
// MidiPot onsetAmount(channel, 8, 11, bounceTime);

// // Length pot
// MidiPot lengthAmount(channel, 7, 12, bounceTime);

// // Reverb Dry/Wet pot
// MidiPot fxReverbDryWet(channel, 6, 13, bounceTime);

// // Echo Dry/Wet pot
// MidiPot fxEchoDryWet(channel, 5, 14, bounceTime);

// // FX Fade pot
// MidiPot fxFade(channel, 11, 4, bounceTime);

// // FX Rate pot
// MidiPot fxRate(channel, 12, 3, bounceTime);


//// Outputs

// LED indicator
// MidiCC autoPlayLED(channel, 12);


void setup() {
    Serial.begin(115200);
    while (!Serial);
    MIDI.begin();
    Serial.println("Arduino ready.");
}

void loop() {
    // if (arpRate.update()) {
    //     usbMIDI.sendControlChange(arpRate.cc.channel, arpRate.read(), arpRate.cc.control);
    //     SERIAL_DEBUG_MIDI(arpRate.cc, arpRate.read());
    // }
    arpRate.readAndSend();



    // usbMIDI.sendNoteOn(note, velocity, channel);
    // delay(200);
    // usbMIDI.sendNoteOff(note, velocity, channel);
    while (usbMIDI.read()) {}
    // delay(50);
}
