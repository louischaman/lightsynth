import mido
import lightsynth.light_instrument as inst
import pysimpledmx
import utils.miditools as mt
from utils.dmxtools import * 
from collections import OrderedDict
import copy
import struct
import serial
import time
import utils.arduino_tools as at

from pprint import pprint

note_old = []
light_dict = {0:20}#,1:30,2:40}

#get dmx devices from user input
print("dmx port = ")
dmx_port = user_dmx()

#dmx_port = pysimpledmx.DMXConnection("COM11")

set_light_cheap(dmx_port, 20, (1,0,0))

lights = {}



## stuff for arduino dimmer
print("arduino port = ")
arduino_port = at.user_serial() 
time.sleep(3)

out_array = [0]*10
out_array[8]
out_array[9]
arduino_working = [0,1,2,3,6,7]

def set_light_arduino(dmx_port, root_dmx, light_val):
    out_array[arduino_working[root_dmx-8]] = int(255*light_val[0])

at.send_array(arduino_port, [200]*10)  

for i in range(8):
    lights[i] = {'root_dmx': i, 'func': set_light_bulb}
for i in range(8,(8+6)):
    lights[i] = {'root_dmx': i, 'func': set_light_arduino}



print("on")

# get midi devices from user input
midi_devices = mido.get_input_names()
port_dict = mt.user_midi()

envelope_params = {
    'type':'envelope', 
    'level':1, 
    'attack':0.1, 
    'decay':2, 
    'sustain':1, 
    'release':2,
    'lfo_level':0,
    'lfo_rate':1,
    'env_mode':"exponential"
}
cc_controls = {
    1: "lfo_rate",
    2: "lfo_level",
    3: "saturation",
    4: "hue",
    6: "level",
    7: "mode",
    
    103: "attack",
    104: "decay",
    107: "sustain",
    108: "release"}

instrument = inst.LightInstrument( 
    #note_list=[48,37],#,38,39,44,45,46], 
    note_list=lights.keys(),
    light_list=lights.keys(), 
    cc_controls = cc_controls,
    envelope_params = envelope_params,
    mode = "cycle" )


modes_ind = 1

instrument_rack = [instrument]

while 1:
    for device, midi_port in port_dict.iteritems():

        # if two cc messages with the same control and channel have come then only append most recent
        message_queue = mt.iter_pending_clean(midi_port)
            
        for msg in message_queue:
            
            print(msg)
            for inst in instrument_rack:
                if msg.type in ["note_on", "note_off"]:
                    msg.note = msg.note % len(lights)
                inst.midi_action(msg)
            
            if msg.type == "control_change":
                if msg.control == 118 and msg.value == 127:
                    modes_ind = (modes_ind + 1 ) % 3
                    print("change mode to " + instrument_rack[0].modes[modes_ind])
                    instrument_rack[0].set_mode( instrument_rack[0].modes[modes_ind])

    light_vals = instrument_rack[0].get_light_output()
    
    for light_key, light in lights.iteritems():
        val = light_vals[light_key] # [ light_vals2[light_key][i] + light_vals[light_key][i] for i in range(3)] 
        
        #val = [col/max_val for col in val]
        light['func'](dmx_port, light['root_dmx'], val)
    print(out_array)
    at.send_array(arduino_port, out_array)
    #dmx_port.render()