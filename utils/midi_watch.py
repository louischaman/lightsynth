import mido
from pprint import pprint
import miditools as mt

midi_ports = mt.user_midi()

while 1:
    for device, midi_port in midi_ports.items():

        # if two cc messages with the same control and channel have come then only append most recent
        for msg in midi_port.iter_pending():
            print(msg)