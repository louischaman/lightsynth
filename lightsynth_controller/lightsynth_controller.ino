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
    Bounce(2, bounceTime),
    Bounce(3, bounceTime),
    Bounce(4, bounceTime),
    Bounce(5, bounceTime),
    Bounce(6, bounceTime),
    Bounce(7, bounceTime),
};
MidiSwitch<decltype(usbMIDI), usbMIDI, selectorSwitchPositions, true> selector(channel, 0, selectorSwitch);

// Auto Play button
MidiButton<decltype(usbMIDI), usbMIDI> autoPlay(channel, 1, 8, bounceTime);

// Arp on/off
MidiButton<decltype(usbMIDI), usbMIDI> arpOnOff(channel, 2, 9, bounceTime);

// Scale on/off
MidiButton<decltype(usbMIDI), usbMIDI> scaleOnOff(channel, 3, 10, bounceTime);

// Sustain on/half/off
constexpr auto sustainAmountPositions {2};
const std::array<Bounce, sustainAmountPositions> sustainAmount {
    Bounce(11, bounceTime),
    Bounce(12, bounceTime),
};
MidiSwitch<decltype(usbMIDI), usbMIDI, sustainAmountPositions, true> sustain(channel, 4, sustainAmount);

// FX on/off
MidiButton<decltype(usbMIDI), usbMIDI> fxOnOff(channel, 5, 14, bounceTime);



// Arp rate pot
MidiPot<decltype(usbMIDI), usbMIDI> arpRate(channel, 3, 9);

// Onset pot
MidiPot<decltype(usbMIDI), usbMIDI> onsetAmount(channel, 6, 8);

// Length pot
MidiPot<decltype(usbMIDI), usbMIDI> lengthAmount(channel, 7, 7);

// Reverb Dry/Wet pot
MidiPot<decltype(usbMIDI), usbMIDI> fxReverbDryWet(channel, 9, 6);

// Echo Dry/Wet pot
MidiPot<decltype(usbMIDI), usbMIDI> fxEchoDryWet(channel, 10, 5);

// FX Fade pot
MidiPot<decltype(usbMIDI), usbMIDI> fxFade(channel, 11, 4);

// FX Rate pot
MidiPot<decltype(usbMIDI), usbMIDI> fxRate(channel, 12, 3);


//// Outputs

// LED indicator
// MidiCC autoPlayLED(channel, 12);


void setup() {
    Serial.begin(115200);
    while (!Serial);
    MIDI.begin();
    Serial.println("Arduino ready.");

    for (auto i = 2; i != 15; ++i) { pinMode(i, INPUT_PULLUP); }
}

void loop() {
    selector.readAndSend();
    autoPlay.readAndSend();

    arpRate.readAndSend();
    arpOnOff.readAndSend();
    scaleOnOff.readAndSend();

    onsetAmount.readAndSend();
    lengthAmount.readAndSend();
    sustain.readAndSend();

    fxOnOff.readAndSend();
    fxReverbDryWet.readAndSend();
    fxEchoDryWet.readAndSend();
    fxFade.readAndSend();
    fxRate.readAndSend();




    // usbMIDI.sendNoteOn(note, velocity, channel);
    // delay(200);
    // usbMIDI.sendNoteOff(note, velocity, channel);
    while (usbMIDI.read()) {}
    delay(50);
}
