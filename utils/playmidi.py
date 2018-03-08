import miditools as mt
import mido
import time
boop = mido.Message('note_on', note=60)
tick = mido.Message('note_on', note=60)
midi_port = mt.user_midi_output().values()[0]

print(midi_port)
while 1:
    for i in range(4):
        if i == 0:
            print("boop")
            midi_port.send(boop)
        else:
            print("tick")
            midi_port.send(tick)
        time.sleep(0.5)