import mido
from pprint import pprint
import utils.miditools as mt
from utils.midi_arpegiator import arpeggiator 
import time
import random
import utils.generate_scale_mapping as scalemap


## to do
# parameter change does not turn off auto
# get note bend to come through
# velocity effects light levels

out_dict = mt.user_midi_output()

note_store = mt.note_store()
note_store_auto = mt.note_store()
rand_note_time = 1
arp_on = True

time_before_random = 0

mapping = scalemap.generate_scale_mapping(scalemap.scales['roro'])


arp = arpeggiator(rate = 120*4)
last_played_time = time.time()
last_auto_time = time.time()

program_int = 0
n_sounds = 32 + 1

def cc_scaler(xmin,xmax):
    return (lambda x: (float(x)/127) * (xmax - xmin) + xmin)

arp_rate = cc_scaler(120,120*12)

print(arp_rate(100))
#arp.randomise_order()

def send_msg(midi_out_port, msg):
    print(msg)
    midi_out_port.send(msg)


while 1:
    for device, midi_out_port in out_dict.items():

        if  (last_auto_time + rand_note_time) < time.time() and not note_store.any_notes_on():
            rand_note_time = float(random.randrange(1,4))
            last_auto_time = time.time()

            if random.random() < 0.5 or len(note_store_auto.which_notes_on()) > 4:
                for note in note_store_auto.which_notes_on():
                    msg = mido.Message("note_off",note = note )
                    note_store_auto.on_msg(msg)
                    send_msg(midi_out_port, msg)
            
            rand_note = random.randrange(40, 90, 1)
            while rand_note in note_store_auto.which_notes_on():
                rand_note = random.randrange(40, 90, 1)

            msg = mido.Message("note_on",note = rand_note, velocity = int(random.random()*127) )
            
            msg = mt.map_note(mapping, msg)
            note_store_auto.on_msg(msg)
            send_msg(midi_out_port, msg)

