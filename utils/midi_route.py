import mido
from pprint import pprint
import miditools as mt

port_dict = mt.user_midi()

out_dict = mt.user_midi_output()

while 1:
    for device, midi_port_in in port_dict.items():
        for device, midi_out_port in out_dict.items():

            # if two cc messages with the same control and channel have come then only append most recent
            for msg in midi_port_in.iter_pending():
                print(msg)
                
                midi_out_port.send(msg)