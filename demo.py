import mido
import lightsynth.light_instrument as inst
import pysimpledmx
import utils.miditools as mt
from utils.dmxtools import * 
from collections import OrderedDict

from pprint import pprint

note_old = []
light_dict = {0:20}#,1:30,2:40}

#get dmx devices from user input
dmx_port = user_dmx()

#dmx_port = pysimpledmx.DMXConnection("COM11")


lights = {    
    0:{'root_dmx': 20, 'func': set_big_light},
    1:{'root_dmx': 30, 'func': set_light_cheap}
}


print("on")

# get midi devices from user input
midi_devices = mido.get_input_names()
port_dict = mt.user_midi()

envelope_params = {
    'type':'envelope', 
    'level':1, 
    'attack':2, 
    'decay':2, 
    'sustain':1, 
    'release':2,
    'lfo_level':0,
    'lfo_rate':1
}
cc_controls = {
    1: "lfo_rate",
    2: "lfo_level",
    3: "saturation",
    4: "hue",
    5: "sustain",
    6: "level",
    26: 'mode'}

instrument = inst.LightInstrument( 
    note_list=[60,62], 
    light_list=lights.keys(), 
    cc_controls = cc_controls,
    note_channel = 1,
    envelope_params = envelope_params,
    mode = "cycle" )

instrument2 = inst.LightInstrument( 
    light_list=lights.keys(), 
    mode="all", 
    rgb=(1,1,1), 
    envelope_params = envelope_params,
    note_channel = 0 )

instrument_rack = [instrument, instrument2]

while 1:
    for device, midi_port in port_dict.items():

        # if two cc messages with the same control and channel have come then only append most recent
        message_queue = mt.iter_pending_clean(midi_port)
            
        for msg in message_queue:
            print(msg)
            for inst in instrument_rack:
                inst.midi_action(msg)
            
    light_vals = instrument_rack[0].get_light_output()
    light_vals2 = instrument_rack[1].get_light_output()
    for light_key, light in lights.items():
        val = [ light_vals2[light_key][i] + light_vals[light_key][i] for i in range(3)] 
        light['func'](dmx_port, light['root_dmx'], val)