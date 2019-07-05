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

set_light_cheap(dmx_port, 10, (1,0,0))
lights = {    
    0:{'root_dmx': 10, 'func': set_big_light},
    1:{'root_dmx': 20, 'func': set_big_light},
    2:{'root_dmx': 30, 'func': set_big_light},
    3:{'root_dmx': 40, 'func': set_big_light},
    4:{'root_dmx': 50, 'func': set_big_light}
}
strobe_lights = { #set_light_cheap
    1:{'root_dmx':  1, 'func': set_effect}
}

switch_light = { #set_light_cheap
    1:{'root_dmx':  60, 'func': set_effect}
}

# bottom left to right
notes_1 = [ 36, 37, 38, 39, 40]
# top left to right
notes_2 = [ 44, 45, 46, 47, 48]

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
    16: "saturation",
    0: "hue",
    5: "sustain",
    12: "level",
    8: "attack",
    20: "decay",
    24: "sustain",
    4: "release"}

# to make twister work for down press
from_cc = [mido.Message('control_change', control=note_here, channel=4, value=127) for note_here in range(0,8)]
to_cc   = [mido.Message('control_change', control=note_here+16, channel=0, value=127) for note_here in range(0,8)]
mapping = dict(zip(from_cc, to_cc))

blackout_on = False
def off_trigger(blackout_on, msg):
    if msg.type == "note_on":
        if msg.note == 60:
            print("blackout")
            return not blackout_on
    
    return blackout_on




instrument = inst.LightInstrument( 
    note_list=notes_1, 
    light_list=lights.keys(), 
    cc_controls = cc_controls,
    note_channel = 0,
    envelope_params = envelope_params,
    mode = "single" )

cc_controls_2 = dict()
for key, value in cc_controls.items():
    cc_controls_2[key+1] = value

instrument2 = inst.LightInstrument( 
    note_list=notes_2, 
    light_list=lights.keys(), 
    mode="single", 
    rgb=(1,1,1), 
    envelope_params = copy.copy(envelope_params),
    cc_controls = cc_controls_2,
    note_channel = 0 
    )


effect_inst = inst.LightEffects( 
    switch_notes=[66], # bottom right midifighter
    trigger_note=[51], # top right beatstep
    on_notes = [50],
    light_type="martin",
    
    cc_controls = {15: "brightness",11: "rate", 7: "duration", 3: 'effect'}
    )

switch_inst = inst.LightSwitch([42], [43], 0)

instrument_rack = [instrument, instrument2, effect_inst, switch_inst]

whole_secs = int(time.time())
n_frames = 0
while 1:
    n_frames = n_frames + 1

    for device, midi_port in port_dict.items():

        # if two cc messages with the same control and channel have come then only append most recent
        message_queue = mt.iter_pending_clean(midi_port)
            
        for msg in message_queue:
            msg = mt.change_cc(mapping, msg)
            print(msg)

            blackout_on = off_trigger(blackout_on, msg)

            for inst in instrument_rack:
                inst.midi_action(msg)

            
    light_vals = instrument_rack[0].get_light_output()
    light_vals2 = instrument_rack[1].get_light_output()
    strobe_val = instrument_rack[2].get_light_output()
    switch_val = instrument_rack[3].get_light_output()

    light_vals = np.add( np.array(light_vals.values()), np.array(light_vals2.values()))
    maxes = np.maximum( np.max(light_vals,1), 1)
    light_vals_scaled = light_vals/maxes[:,np.newaxis]
    light_vals_scaled = light_vals_scaled.tolist()
    #light_vals_scaled.append(strobe_vals)

    for light_key, light in lights.items():
        val = light_vals_scaled[light_key]
        if blackout_on:
            val = [0.0, 0.0, 0.0]
        light['func'](dmx_port, light['root_dmx'], val  )

    for light_key, strobe in strobe_lights.items():
        strobe['func'](dmx_port, strobe['root_dmx'], strobe_val)

        
    for light_key, switch in switch_light.items():
        switch['func'](dmx_port, switch['root_dmx'], [switch_val[0]*255] )


    dmx_port.render()

    # if time.time()>whole_secs + 1:
    #     whole_secs = time.time()
    #     print(n_frames)
    #     n_frames = 0

    
