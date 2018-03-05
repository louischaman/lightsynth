import mido
import lightsynth.light_instrument as inst
import pysimpledmx

from utils.list_ports import serial_ports
from collections import OrderedDict

from pprint import pprint

note_old = []

def set_dmx(dmx_port, channel, level):
    # doesnt go above 255 or below 0
    level = min(level,255)
    level = max(level,0)
    try:
        dmx_port.setChannel(channel, int(level) ) 
        dmx_port.render()
    except Exception as error:
        pprint(channel, level)
        raise(error)


light_dict = {0:20,1:30,2:40}

def set_light_cheap(dmx_port, light_channel, rgb):
    # set position one (level) to max
    set_dmx(dmx_port, light_channel, 255)

    for i, col_lev in enumerate(rgb):
        set_dmx(dmx_port, light_channel + i + 1, col_lev )

# get dmx devices from user input
# available_ports = serial_ports()
# if len(available_ports ) > 0:
#     pprint([ (i, available_ports[i]) for i in range(len(available_ports))] )
#     which_port = int(raw_input('select port number: '))
    
#     dmx_port = dmx.DMXConnection(available_ports[which_port])
# else:
#     print("no_dmx")
#     dmx_port = None


dmx_port = pysimpledmx.DMXConnection("COM11")

set_dmx(dmx_port, 1, 255)
set_dmx(dmx_port, 2, 255)

set_light_cheap(dmx_port, 20, (255,0,0))
set_light_cheap(dmx_port, 30, (255,0,0))
set_light_cheap(dmx_port, 40, (255,0,0))

print("on")

# get midi devices from user input
midi_devices = mido.get_input_names()
port_dict = {}
while True:
    pprint([ (i, midi_devices[i]) for i in range(len(midi_devices))] )
    user_input = raw_input('select midi device number: ')
    pprint(midi_devices)
    if user_input is "" or midi_devices is []:
        break
    try:
        which_device = int(user_input)
        device_name = midi_devices.pop(which_device)
        inport = mido.open_input(device_name)
        port_dict[device_name] = inport
    except:
        print("please enter an into or nothing to continue")


instrument = inst.LightInstrument( note_list=range(126), light_list=light_dict.keys() )

while 1:
    for device, midi_port in port_dict.iteritems():

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
            
        for msg in message_queue:
            print(msg)
            if(msg.type == "control_change"):
                pass

            elif(msg.type == "note_on" or msg.type == "note_off"):
                instrument.note_action(msg)
            
    light_vals = instrument.get_light_output()
    for light, channel in light_dict.iteritems():
        val = light_vals[light]
        set_light_cheap(dmx_port, channel, val)