import mido
from pprint import pprint
import utils.miditools as mt
from utils.midi_arpegiator import arpeggiator 
import time
import random
import utils.generate_scale_mapping as scalemap
from collections import deque


## to do
# parameter change does not turn off auto
# get note bend to come through
# velocity effects light levels

port_dict = mt.user_midi()
out_dict = mt.user_midi_output()

note_store = mt.note_store()
note_store_auto = mt.note_store()
rand_note_time = 1
arp_on = True

time_before_random = 1000

mapping = scalemap.generate_scale_mapping(scalemap.scales['rosy'])


arp = arpeggiator(rate = 120*4)
last_played_time = time.time()
last_auto_time = time.time()

program_int = 0
n_sounds = 32 + 1
speed = 1

def cc_scaler(xmin,xmax):
    return (lambda x: (float(x)/127) * (xmax - xmin) + xmin)

arp_rate = cc_scaler(120,120*12)

print(arp_rate(100))
#arp.randomise_order()

def send_msg(midi_out_port, msg):
    print(msg)
    midi_out_port.send(msg)

class note_seq_trigger:
    def __init__(self, trigger_seq, time_before_deactivate):
        self.trigger_seq = trigger_seq
        self.note_buffer = deque(maxlen= len(trigger_seq))
        self.trigger_active = False
        self.time_before_deactivate = time_before_deactivate

    def on_msg(self, note):
        self.time_since_actve = time.time()
        if msg.type == "note_on":
            self.note_buffer.append(msg.note)
            print(list(self.note_buffer))
            
        if self.trigger_active:
            if msg.type == 'control_change':
                if msg.control == 16:
                    self.trigger_active = False
                    print("######### Deactivate ###########")
                    send_msg(midi_out_port, mido.Message('control_change', control=16, value=0, channel  = 3) )
                    send_msg(midi_out_port, mido.Message('note_on',note = 124) )
                    time.sleep(0.001)
                    send_msg(midi_out_port, mido.Message('note_off',note = 124) )

    def run(self, midi_out_port):
        if list(self.note_buffer) == self.trigger_seq:
            self.note_buffer.clear()
            self.trigger_active = True
            print("######### Activate ###########")
            time.sleep(1)
            send_msg(midi_out_port, mido.Message('control_change', control=16, value=127, channel  = 3) )
            send_msg(midi_out_port, mido.Message('note_on',note = 122) )
            send_msg(midi_out_port, mido.Message('note_on',note = 121) )
            time.sleep(0.001)
            send_msg(midi_out_port, mido.Message('note_off',note = 122) )
            send_msg(midi_out_port, mido.Message('note_off',note = 121) )

        if self.trigger_active:
            if time.time() > (self.time_since_actve + self.time_before_deactivate ):
                self.trigger_active = False
                print("######### Deactivate ###########")
                send_msg(midi_out_port, mido.Message('control_change', control=16, value=0, channel  = 3) )
                send_msg(midi_out_port, mido.Message('note_on',note = 124) )
                time.sleep(0.001)
                send_msg(midi_out_port, mido.Message('note_off',note = 124) )

        
                
            

note_trigger = note_seq_trigger([60, 60, 60, 62, 60, 60, 55, 57, 55, 57, 59, 60, 60], 20)
prob_off = 0.25

while 1:
    for device, midi_port_in in port_dict.items():
        for device, midi_out_port in out_dict.items():

            if (last_played_time + time_before_random) < time.time() and (last_auto_time + rand_note_time) < time.time() and not note_store.any_notes_on():
                rand_note_time = float(random.randrange(1,4)) * speed
                last_auto_time = time.time()

                if random.random() < prob_off or len(note_store_auto.which_notes_on()) > 4:
                    for note in note_store_auto.which_notes_on():
                        msg = mido.Message("note_off",note = note )
                        note_store_auto.on_msg(msg)
                        send_msg(midi_out_port, msg)


                rand_note = random.randrange(40, 90, 1)
                while rand_note in note_store_auto.which_notes_on():
                    rand_note = random.randrange(40, 90, 1)

                msg = mido.Message("note_on",note = random.randrange(40, 90, 1), velocity = random.randrange(40, 127, 1) )
                
                msg = mt.map_note(mapping, msg)
                note_store_auto.on_msg(msg)
                send_msg(midi_out_port, msg)

            note_trigger.run(midi_out_port)

            # if two cc messages with the same control and channel have come then only append most recent
            for msg in mt.iter_pending_clean(midi_port_in):
                note_store.on_msg(msg)

                # sends a trigger if sequence is played
                note_trigger.on_msg(msg)
                

                if msg.type in ["note_on", "note_off"]:
                    last_played_time = time.time()

                    # if note pressed turn all auto notes off
                    for note in note_store_auto.which_notes_on():
                        msg_off = mido.Message("note_off",note = note )
                        note_store_auto.on_msg(msg_off)
                        send_msg(midi_out_port, msg_off)

                    send_msg(midi_out_port, msg)

                # if msg.type == "control_change":
                #     if msg.control == 26:
                #         arp.rate = arp_rate(msg.value)
                #     elif msg.control == 113 and msg.value == 127:
                #         arp_on = not arp_on
                #     elif msg.control == 114 and msg.value == 127:
                #         program_int = (program_int - 1) % n_sounds
                #         msg = mido.Message("program_change", program = program_int)
                #         send_msg(midi_out_port, msg)
                #     elif msg.control == 115 and msg.value == 127:
                #         program_int = (program_int + 1) % n_sounds
                #         msg = mido.Message("program_change", program = program_int)
                #         send_msg(midi_out_port, msg)
                #     else:
                #         send_msg(midi_out_port, msg)

                if msg.type == "control_change":
                    send_msg(midi_out_port, msg)
                        
                if msg.type == "pitchwheel":
                    send_msg(midi_out_port, msg)