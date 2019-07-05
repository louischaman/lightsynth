import miditools as mt
import mido
import time
boop = mido.Message('note_on', note=61)
tick = mido.Message('note_on', note=60)
midi_port = mt.user_midi_output().values()[0]

print(midi_port)
note_time = 0.0001



from_cc = [mido.Message('control_change', control=note_here, channel=4, value=127) for note_here in range(0,4)]
to_cc   = [mido.Message('control_change', control=note_here+16, channel=0, value=127) for note_here in range(0,4)]


while 1:
    for i in range(4):
        if i == 0:
            print("boop")
            midi_port.send(mido.Message('note_on', note=61))
            time.sleep(note_time)
            midi_port.send(mido.Message('note_off', note=61))
        else:
            print("tick")
            midi_port.send(mido.Message('note_on', note=60))
            time.sleep(note_time)
            midi_port.send(mido.Message('note_off', note=60))
        time.sleep(0.1)