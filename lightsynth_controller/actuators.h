#ifndef MIDI_ACTUATORS_H
#define MIDI_ACTUATORS_H


#include <array>

// Struct that carries the midi channel and control.
struct MidiCC {
    const uint8_t channel;
    const uint8_t control;

    MidiCC(uint8_t _channel, uint8_t _control) : channel(_channel), control(_control) {}
};


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

// TODO: Apply hysteresis.
class MidiPot {
public:
    const MidiCC cc;
private:
   const uint8_t adcChannel;

public:
    MidiPot(const uint8_t channel, const uint8_t control, const uint8_t pin, const uint8_t debounceTimeMillis) : cc(channel, control), adcChannel(pin) {}

    uint8_t read() const { const uint32_t value = analogRead(adcChannel); return value >> 3; }
};


#endif /* MIDI_ACTUATORS_H */
