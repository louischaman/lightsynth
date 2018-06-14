import mido
from pprint import pprint
from collections import OrderedDict


def same_message(note_a, note_b):
    is_same = (note_a.control == note_b.control) and (note_a.channel == note_b.channel) and (note_a.type == note_b.type) and (note_a.value == note_b.value)
    return(is_same)


def same_channel_control(note_a, note_b):
    is_same = (note_a.control == note_b.control) and (note_a.channel == note_b.channel) and (note_a.type == note_b.type) 
    return(is_same)

def toggle_cc(status, msg):
    for cc, value in status.iteritems():
        if same_message(cc, msg):
            value = (not value) * 127
            msg.value = value
            break
    return(msg)

def change_cc(mapping, msg):
    if msg.type == "control_change":
        for cc_from, cc_to in mapping.iteritems():
            if same_channel_control(cc_from, msg):

                msg.channel = cc_to.channel
                msg.control = cc_to.control
                break
    return(msg)

def map_note(mapping, msg):
    if msg.type == "note_on" or msg.type == "note_off":
        try:
            msg.note = mapping[msg.note]
        except:
            pass
    return(msg)


def user_midi():
    midi_devices = mido.get_input_names()
    port_dict = {}
    for i in range(len(midi_devices)):
        pprint((i, midi_devices[i]) )
    while True:
        user_input = raw_input('select midi device number: ')
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

def user_midi_output():
    midi_devices = mido.get_output_names()
    port_dict = {}
    for i in range(len(midi_devices)):
        pprint((i, midi_devices[i]) )
    while True:
        user_input = raw_input('select midi device number: ')
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



def iter_pending_clean(midi_port, clean_velocity = True):
        # if two cc messages with the same control and channel have come then only append most recent
    message_queue = OrderedDict({})
    msg_no = 0
    for msg in midi_port.iter_pending():                        
        if(msg.type == "control_change"):
            key = str(msg.control) + " - " + str(msg.channel)
            message_queue[key] = msg

        
        if(msg.type == "note_on" or msg.type == "note_off"):
            if clean_velocity and msg.velocity == 0:
                msg = mido.Message('note_off', channel = msg.channel, note = msg.note)

            message_queue[msg_no] = msg

        
        msg_no = msg_no + 1
        
    message_queue = message_queue.values()
    return message_queue