#ifndef MIDI_ACTUATORS_H
#define MIDI_ACTUATORS_H


#include <array>

namespace
{
inline uint32_t getAbsDiff(uint32_t a, uint32_t b)
{
    return (a > b) ? (a - b) : (b - a);
}
}

// Struct that carries the midi channel and control.
struct MidiCC {
    const uint8_t channel;
    const uint8_t control;

    MidiCC(uint8_t _channel, uint8_t _control) : channel(_channel), control(_control) {}
};

void SERIAL_DEBUG_MIDI(const MidiCC cc, const uint_fast8_t value) {
        Serial.print("Ch: ");
        Serial.print(cc.channel);
        Serial.print(" Ctrl: ");
        Serial.print(cc.control);
        Serial.print(" Val: ");
        Serial.println(value);
}

class MidiButton {
public:
    const MidiCC cc;
private:
    Bounce button;

public:
    MidiButton(const uint8_t channel, const uint8_t control, const uint8_t pin, const uint8_t debounceTimeMillis) : cc(channel, control), button(pin, debounceTimeMillis) {}

    bool read() { button.update(); return button.read(); }
};


template<uint8_t n_positions>
class MidiSwitch {
public:
    const MidiCC cc;
private:
    const std::array<Bounce, n_positions> positions;

public:
    MidiSwitch(const uint8_t channel, const uint8_t control, std::array<Bounce, n_positions> _positions) 
        : cc(channel, control), positions(_positions) {}
    
    uint8_t read() const {
        auto position {0U};
        for(auto &position: positions) {
            if (position.read()) { break; }
            ++position;
        }
        return position;
    }
};

template<class MIDI_T, MIDI_T& midi>
class MidiPot {
public:
    const MidiCC cc;
private:
   const uint8_t adcChannel;
   uint32_t value;

public:
    MidiPot(const uint8_t channel, const uint8_t control, const uint8_t pin) : cc(channel, control), adcChannel(pin) {}

    bool update() { 
        // Average the pot output for some noise immunity.
        const uint32_t newValue1 = analogRead(adcChannel);
        const uint32_t newValue2 = analogRead(adcChannel);
        const uint32_t newValue3 = analogRead(adcChannel);
        const uint32_t newValue4 = analogRead(adcChannel);

        const auto newValue = (newValue1 + newValue2 + newValue3 + newValue4) >> 2;


        // Update value if it is new and return true.
        // Builds in some hysterysis to avoid spamming too much.
        if (getAbsDiff(newValue, value) >= 10) {
            value = newValue;
            return true;
        }
        return false;
    }
    uint8_t read() const { return (value >> 3); }

    void readAndSend() {
        if (update()) {
            const auto ccVal = read();
            midi.sendControlChange(cc.channel, ccVal, cc.control);
            SERIAL_DEBUG_MIDI(cc, ccVal);
        }
    }
};


#endif /* MIDI_ACTUATORS_H */
