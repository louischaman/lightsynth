import mido
import lightsynth.light_instrument as inst
import pysimpledmx
import utils.miditools as mt
from utils.dmxtools import * 
from collections import OrderedDict
import copy
import numpy as np
import time

from pprint import pprint

note_old = []
light_dict = {0:20}#,1:30,2:40}

#get dmx devices from user input
dmx_port = user_dmx()

#dmx_port = pysimpledmx.DMXConnection("COM11")

set_light_cheap(dmx_port, 20, (1,0,0))
lights = {    
    0:{'root_dmx': 10, 'func': set_light_cheap},
    1:{'root_dmx': 20, 'func': set_light_cheap},
    2:{'root_dmx': 30, 'func': set_light_cheap},
    3:{'root_dmx': 40, 'func': set_light_cheap},
    4:{'root_dmx': 50, 'func': set_light_cheap},
    5:{'root_dmx': 70, 'func': set_big_light},
    6:{'root_dmx': 80, 'func': set_big_light} #set_light_cheap
}




print("on")

# get midi devices from user input
midi_devices = mido.get_input_names()
port_dict = mt.user_midi()

envelope_params = {
    'type':'envelope', 
    'level':1, 
    'attack':0, 
    'decay':0.5, 
    'sustain':1, 
    'release':0.04,
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
    note_list=[60,61],#38,39,44,45,46], 
    light_list=lights.keys(), 
    cc_controls = cc_controls,
    #note_channel = 1,
    envelope_params = envelope_params,
    mode = "all" )

instrument2 = inst.LightInstrument( 
    note_list=[40,41],#,42,43,47,48,49], 
    light_list=lights.keys(), 
    mode="all", 
    rgb=(1,1,1), 
    envelope_params = copy.copy(envelope_params),
    cc_controls = cc_controls
    #note_channel = 0 
    )

instrument_rack = [instrument, instrument2]

whole_secs = int(time.time())
n_frames = 0
while 1:
    n_frames = n_frames + 1

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
    light_vals = np.add( np.array(light_vals.values()), np.array(light_vals2.values()))
    maxes = np.maximum( np.max(light_vals,1), 1)
    light_vals_scaled = light_vals/maxes[:,np.newaxis]

    for light_key, light in lights.iteritems():
        val = light_vals_scaled[light_key,].tolist()
        light['func'](dmx_port, light['root_dmx'], val)
    dmx_port.render()

    if time.time()>whole_secs + 1:
        whole_secs = time.time()
        print(n_frames)
        n_frames = 0

    
