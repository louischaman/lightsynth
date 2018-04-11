import mido
import lightsynth.light_instrument as inst
import pysimpledmx
import utils.miditools as mt
from utils.dmxtools import * 
from collections import OrderedDict
import copy

from pprint import pprint

note_old = []
light_dict = {0:20}#,1:30,2:40}

#get dmx devices from user input
dmx_port = user_dmx()

#dmx_port = pysimpledmx.DMXConnection("COM11")

set_light_cheap(dmx_port, 20, (1,0,0))
lights = {    
    0:{'root_dmx': 0, 'func': set_light_bulb},
    1:{'root_dmx': 1, 'func': set_light_bulb}
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
    'lfo_rate':1,
    'env_mode':"exponential"
}
cc_controls = {
    1: "lfo_rate",
    2: "lfo_level",
    3: "saturation",
    4: "hue",
    5: "sustain",
    6: "level",
    
    7: "attack",
    8: "decay",
    9: "sustain",
    10: "release",
    11: 'mode'}

instrument = inst.LightInstrument( 
    #note_list=[48,37],#,38,39,44,45,46], 
    light_list=lights.keys(), 
    cc_controls = cc_controls,
    note_channel = 0,
    envelope_params = envelope_params,
    mode = "cycle" )

instrument2 = inst.LightInstrument( 
    note_list=[40,60],#41,42,43,47,48,49], 
    light_list=lights.keys(), 
    mode="single", 
    rgb=(1,1,1), 
    envelope_params = copy.copy(envelope_params),
    cc_controls = cc_controls,
    note_channel = 1
    )

instrument_rack = [instrument, instrument2]

while 1:
    for device, midi_port in port_dict.iteritems():

        # if two cc messages with the same control and channel have come then only append most recent
        message_queue = mt.iter_pending_clean(midi_port)
            
        for msg in message_queue:
            print(msg)
            if msg.type == "control_change":
                if msg.channel in range(0,len(instrument_rack)):
                    instrument_rack[msg.channel].midi_action(msg)
            else:
                for inst in instrument_rack:
                    inst.midi_action(msg)

            
    light_vals = instrument_rack[0].get_light_output()
    light_vals2 = instrument_rack[1].get_light_output()

    for light_key, light in lights.iteritems():
        val = [ light_vals2[light_key][i] + light_vals[light_key][i] for i in range(3)] 
        max_val = max(val)
        max_val = max(1, max_val)
        
        val = [col/max_val for col in val]
        light['func'](dmx_port, light['root_dmx'], val)