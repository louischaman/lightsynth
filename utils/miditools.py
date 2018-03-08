import mido
from pprint import pprint
from collections import OrderedDict

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



def iter_pending_clean(midi_port):
        # if two cc messages with the same control and channel have come then only append most recent
    message_queue = OrderedDict({})
    msg_no = 0
    for msg in midi_port.iter_pending():                        
        if(msg.type == "control_change"):
            key = str(msg.control) + " - " + str(msg.channel)
            message_queue[key] = msg

        
        if(msg.type == "note_on" or msg.type == "note_off"):
            message_queue[msg_no] = msg

        
        msg_no = msg_no + 1
        
    message_queue = message_queue.values()
    return message_queue