import miditools as mt
import mido
import time
boop_note = 22
tick_note = 23
midi_port = mt.user_midi_output().values()[0]

print(midi_port)
note_time = 0.0001
while 1:
    for i in range(4):
        if i == 0:
            print("boop")
            midi_port.send(mido.Message('note_on', note=boop_note))
            time.sleep(note_time)
            midi_port.send(mido.Message('note_off', note=boop_note))
        else:
            print("tick")
            midi_port.send(mido.Message('note_on', note=tick_note))
            time.sleep(note_time)
            midi_port.send(mido.Message('note_off', note=tick_note))
        time.sleep(0.1)