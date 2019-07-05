import mido
from pprint import pprint

midi_devices = mido.get_input_names()
port_dict = {}

import miditools as mt


from_cc = [mido.Message('control_change', control=note_here, channel=4, value=127) for note_here in range(0,4)]
to_cc   = [mido.Message('control_change', control=note_here+16, channel=0, value=127) for note_here in range(0,4)]
mapping = dict(zip(from_cc, to_cc))

while True:
    pprint([ (i, midi_devices[i]) for i in range(len(midi_devices))] )
    user_input = input('select midi device number: ')
    print(midi_devices)
    if user_input is "" or midi_devices is []:
        break
    try:
        which_device = int(user_input)
        device_name = midi_devices.pop(which_device)
        inport = mido.open_input(device_name)
        port_dict[device_name] = inport
    except:
        print("please enter an into or nothing to continue")

while 1:
    for device, midi_port in port_dict.items():

        # if two cc messages with the same control and channel have come then only append most recent
        for msg in midi_port.iter_pending():
            msg = mt.change_cc(mapping, msg)
            print(msg)