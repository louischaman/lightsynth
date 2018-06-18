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

port_dict = mt.user_midi()
out_dict = mt.user_midi_output(1)

note_store = mt.note_store()
note_store_auto = mt.note_store()
rand_note_time = 1
arp_on = True

time_before_random = 5

mapping = scalemap.generate_scale_mapping(scalemap.scales['roro'])


arp = arpeggiator(rate = 120*4)
last_played_time = time.time()
last_auto_time = time.time()

def cc_scaler(xmin,xmax):
    return (lambda x: (float(x)/127) * (xmax - xmin) + xmin)

arp_rate = cc_scaler(120,120*12)

print(arp_rate(100))
#arp.randomise_order()

def send_msg(midi_out_port, msg):
    print(msg)
    midi_out_port.send(msg)



while 1:
    for device, midi_port_in in port_dict.iteritems():
        for device, midi_out_port in out_dict.iteritems():

            if (last_played_time + time_before_random) < time.time() and (last_auto_time + rand_note_time) < time.time() and not note_store.any_notes_on():
                rand_note_time = float(random.randrange(1,4))/ 4 
                last_auto_time = time.time()

                if random.random() < 0.5 or len(note_store_auto.which_notes_on()) > 4:
                    for note in note_store_auto.which_notes_on():
                        msg = mido.Message("note_off",note = note )
                        note_store_auto.on_msg(msg)
                        send_msg(midi_out_port, msg)

                msg = mido.Message("note_on",note = random.randrange(40, 90, 1), velocity = int(random.random()*127) )
                
                msg = mt.map_note(mapping, msg)
                note_store_auto.on_msg(msg)
                send_msg(midi_out_port, msg)


            # if two cc messages with the same control and channel have come then only append most recent
            for msg in mt.iter_pending_clean(midi_port_in):
                note_store.on_msg(msg)

                if msg.type in ["note_on", "note_off"]:
                    last_played_time = time.time()

                    for note in note_store_auto.which_notes_on():
                        msg_off = mido.Message("note_off",note = note )
                        note_store_auto.on_msg(msg_off)
                        send_msg(midi_out_port, msg_off)

                if msg.type == "control_change":
                    if msg.control == 101:
                        arp.rate = arp_rate(msg.value)
                    if msg.control == 113 and msg.value == 127:
                        arp_on = not arp_on
                    send_msg(midi_out_port, msg)

                if arp_on:
                    arp.note_msg(msg)
                else:
                    send_msg(midi_out_port, msg)

            if arp_on:
                for msg_out in arp.get_notes():
                    print(msg_out)
                    midi_out_port.send(msg_out)