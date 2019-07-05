import mido
import time
from ..utils.miditools import user_midi

port_dict = user_midi()

msg_1 = mido.Message('note_on', note=note + 50) 
msg_2 = mido.Message('note_on', note=note + 50) 

for device, midi_port_in in port_dict.items():
    midi_port_in.send(msg_1)

time.sleep(1)
for device, midi_port_in in port_dict.items():
    midi_port_in.send(msg_2)