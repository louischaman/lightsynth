import mido
import time
from utils.miditools import user_midi_output

out_dict = user_midi_output()

msg_1 = mido.Message('note_on', note= 50) 
msg_2 = mido.Message('note_on', note=50, velocity = 1) 

for device, midi_port_in in out_dict.items():
    midi_port_in.send(msg_1)

time.sleep(1)

for device, midi_port_in in out_dict.items():
    midi_port_in.send(msg_2)

time.sleep(10)