import mido
from pprint import pprint

midi_devices = mido.get_input_names()
port_dict = {}

while True:
    pprint([ (i, midi_devices[i]) for i in range(len(midi_devices))] )
    user_input = raw_input('select midi device number: ')
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
    for device, midi_port in port_dict.iteritems():

        # if two cc messages with the same control and channel have come then only append most recent
        for msg in midi_port.iter_pending():
            print(msg)