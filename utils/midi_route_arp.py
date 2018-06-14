import mido
from pprint import pprint
import miditools as mt
from midi_arpegiator import arpeggiator 

port_dict = mt.user_midi()

out_dict = mt.user_midi_output()
arp = arpeggiator(rate = 120*4)

while 1:
    for device, midi_port_in in port_dict.iteritems():
        for device, midi_out_port in out_dict.iteritems():

            # if two cc messages with the same control and channel have come then only append most recent
            for msg in mt.iter_pending_clean(midi_port_in):
                arp.note_msg(msg)
                
            for msg_out in arp.get_notes():
                print(arp.notes_on_list())
                print(msg_out)
                midi_out_port.send(msg_out)