#ifndef MIDI_ACTUATORS_H
#define MIDI_ACTUATORS_H


#include <array>

namespace
{
inline uint32_t getAbsDiff(const uint32_t a, const uint32_t b)
{
    return (a > b) ? (a - b) : (b - a);
}

inline uint32_t checkDiff(const uint32_t a, const uint32_t b, const uint32_t maxDiff)
{ 
    return (getAbsDiff(a, b) >= maxDiff);
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

template<class MIDI_T, MIDI_T& midi, bool invert = false>
class MidiButton {
public:
    const MidiCC cc;
private:
    Bounce button;
    bool value {};

public:
    MidiButton(const uint8_t channel, const uint8_t control, const uint8_t pin, const uint8_t debounceTimeMillis) : cc(channel, control), button(pin, debounceTimeMillis) {}

    bool update() {
        button.update();
        const auto newVal = button.read();
        if (newVal != value) {
            value = newVal;
            return true;
        }
        return false;
    }
    inline bool read() const { return invert ? !value : value; }
    void readAndSend()
    {
        if (update()) {
            const auto ccVal = read();
            midi.sendControlChange(cc.control, ccVal, cc.channel);
            SERIAL_DEBUG_MIDI(cc, ccVal);
        }
    }
};


template<
    class MIDI_T, MIDI_T& midi,
    uint8_t n_positions,
    bool invert = false>
class MidiSwitch {
public:
    const MidiCC cc;
private:
    std::array<Bounce, n_positions> positions;
    uint_fast8_t value {};

public:
    MidiSwitch(const uint8_t channel, const uint8_t control, std::array<Bounce, n_positions> _positions) 
        : cc(channel, control), positions(_positions) {}
    
    bool update() {
        auto newValue {0U};
        for(auto &position: positions) {
            position.update();

            const auto rawVal = position.read();
            const auto invertVal = invert ? !rawVal : rawVal;
            if (invertVal) { break; }

            ++newValue;
        }

        if (value != newValue){
            value = newValue;
            return true;
        }
        return false;
    }

    uint8_t read() const { return value; }

    void readAndSend()
    {
        if (update()){
            const auto ccVal = read();
            midi.sendControlChange(cc.control, ccVal, cc.channel);
            SERIAL_DEBUG_MIDI(cc, ccVal);
        }
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
        const auto newValue1 = analogRead(adcChannel);
        delay(1);
        const auto newValue2 = analogRead(adcChannel);
        delay(1);
        const auto newValue3 = analogRead(adcChannel);
        
        // ADC output should be 10-bit, midi cc is 7-bit.
        // Only update value if all three sample values are more than 1 midi cc
        // tick off the old value.
        if (checkDiff(newValue1, value, 8)
                && checkDiff(newValue2, value, 8)
                && checkDiff(newValue3, value, 8)) {
            value = newValue1;
            return true;
        }
        return false;
    }
    uint8_t read() const { return (value >> 3); }

    void readAndSend() {
        if (update()) {
            const auto ccVal = read();
            midi.sendControlChange(cc.control, ccVal, cc.channel);
            SERIAL_DEBUG_MIDI(cc, ccVal);
        }
    }
};


#endif /* MIDI_ACTUATORS_H */
