import mido
from pprint import pprint
from collections import OrderedDict, deque
import copy
import time


def same_message(note_a, note_b):
    is_same = (note_a.control == note_b.control) and (note_a.channel == note_b.channel) and (note_a.type == note_b.type) and (note_a.value == note_b.value)
    return(is_same)


def same_channel_control(note_a, note_b):
    is_same = (note_a.control == note_b.control) and (note_a.channel == note_b.channel) and (note_a.type == note_b.type) 
    return(is_same)

def toggle_cc(status, msg):
    for cc, value in status.items():
        if same_message(cc, msg):
            value = (not value) * 127
            msg.value = value
            break
    return(msg)

def change_cc(mapping, msg):
    if msg.type == "control_change":
        for cc_from, cc_to in mapping.items():
            if same_channel_control(cc_from, msg):

                msg.channel = cc_to.channel
                msg.control = cc_to.control
                break
    return(msg)



def map_note(mapping, msg):
    if msg.type == "note_on" or msg.type == "note_off":
        msg.note = int(mapping[msg.note])
    return(msg)


def user_midi(which_device_ind = None):
    midi_devices = mido.get_input_names()
    port_dict = {}    

    if not which_device_ind is None:
        device_name = midi_devices[which_device_ind]
        inport = mido.open_input(device_name)
        port_dict[device_name] = inport
        return(port_dict)

    for i in range(len(midi_devices)):
        pprint((i, midi_devices[i]) )
    while True:

        user_input = input('select midi device number: ')
        if user_input is "" or midi_devices is []:
            break
        try:
            which_device = int(user_input)
            device_name = midi_devices[which_device]
            inport = mido.open_input(device_name)
            port_dict[device_name] = inport
        except:
            print("please enter an into or nothing to continue")

    return(port_dict)

def user_midi_output(which_device_ind = None):
    midi_devices = mido.get_output_names()
    port_dict = {}
    if not which_device_ind is None:
    
        device_name = midi_devices[which_device_ind]
        inport = mido.open_output(device_name)
        port_dict[device_name] = inport
        return(port_dict)

    for i in range(len(midi_devices)):
        pprint((i, midi_devices[i]) )
    while True:
        
        user_input = input('select midi device number: ')

        if user_input is "" or midi_devices is []:
            break
        try:
            which_device = int(user_input)
            device_name = midi_devices[which_device]
            inport = mido.open_output(device_name)
            port_dict[device_name] = inport
        except:
            print("please enter an into or nothing to continue")

    return(port_dict)



def iter_pending_clean(msg_list, clean_velocity = True):
        # if two cc messages with the same control and channel have come then only append most recent
    message_queue = OrderedDict({})
    msg_no = 0
    for msg in msg_list:    
        if not isinstance(msg, mido.Message):
            message_queue[msg_no] = msg

        if(msg.type == "control_change"):
            key = str(msg.control) + " - " + str(msg.channel)
            message_queue[key] = msg

        
        elif(msg.type == "note_on" or msg.type == "note_off"):
            if clean_velocity and msg.velocity == 0:
                msg = mido.Message('note_off', channel = msg.channel, note = msg.note)

            message_queue[msg_no] = msg

        elif(msg.type == "pitchwheel"):
            message_queue[msg_no] = msg

        msg_no = msg_no + 1
        
    message_queue = message_queue.values()
    return message_queue

class simpleMidiDevice:    
    def on_msg(self, msg):
        if msg.type == "note_on" :
            # if velocity is 0 that is note off in some places
            if msg.velocity == 0:
                self.note_off_action(msg.note)
            else:
                self.note_on_action(msg.note, msg.velocity)
        
        elif msg.type == "note_off":
            self.note_off_action(msg.note)

        elif msg.type == "control_change":
            self.cc_action(msg.control, msg.value)

    def note_on_action(self, note, velocity):
        pass

    def note_off_action(self, note):
        pass

    def cc_action(self, control, value):
        pass

class noteStore(simpleMidiDevice):
    def __init__(self):
        super().__init__()
        self.notes_on = [False] * 128
        self.last_note = [None] * 128
    
    def note_on_action(self, note, velocity):
        self.notes_on[note] = True
        self.last_note[note] = note

    def note_off_action(self, note): 
            self.notes_on[note] = False
            self.last_note[note] = note
    
    def any_notes_on(self):
        return any(self.notes_on)
    
    def which_notes_on(self):
        return [note for note, note_val in enumerate(self.notes_on) if note_val]

    
class noteBuffer(simpleMidiDevice):
    def __init__(self, length):
        super().__init__()
        self.note_buffer = deque(maxlen= length)
    
    def is_equal(self, seq):
        return self.get_last(len(seq)) == seq

    def get_last(self, n = 1):
        return list(self.note_buffer)[len(self.note_buffer)-n:]    
        
    def note_on_action(self, note, velocity):
        self.note_buffer.append(note)

    def count_notes_match(self, seq):
        for i in range(0,len(seq)):
            if self.is_equal(seq[:len(seq)-i]):
                return len(seq) - i
        return 0

    
class midiState(simpleMidiDevice):
    def __init__(self):
        super().__init__()
        notes_cc = dict(zip( range(128), [None] * 128))
        self.note_states = dict(zip( range(16), [copy.copy(notes_cc)] * 16))
        self.cc_states = dict(zip( range(16), [copy.copy(notes_cc)] * 16))
     
    def on_msg(self, msg):

        if msg.type == 'note_on':
            self.note_states[msg.channel][msg.note] = True

        if msg.type == 'note_off':
            self.note_states[msg.channel][msg.note] = False

        if msg.type == "control":
            self.cc_states[msg.channel][msg.control] = msg.value

class midiOutputDevice(simpleMidiDevice):
    def __init__(self, output_port, set_channel=None):
        super().__init__()
        self.output_port = output_port
        self.set_channel = set_channel
        self.note_store = noteStore()
        self.output = True
    
    def on_msg(self, msg):
        if not self.output:
            return
        self.note_store.on_msg(msg)
        if not self.set_channel is None:
            msg = copy.copy(msg)
            msg.channel = self.set_channel
        self.output_port.send(msg)
    
    def switch_channel(self, channel):
        time.sleep(0.1)
        for note in self.note_store.which_notes_on():
            msg = mido.Message('note_off', channel = self.set_channel, note = note)
            self.output_port.send(msg)
        self.set_channel = channel
    
    def toggle_device(self):
        self.output = not self.output


