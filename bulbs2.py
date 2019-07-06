import mido
import lightsynth.light_instrument as inst
import utils.miditools as mt
from utils.dmxtools import * 
from collections import OrderedDict
import copy
import struct
import time
import utils.arduino_tools as at
from pysimpledmx import DMXConnection
import math
import random

from pprint import pprint

max_length_decay = 9
decay_exp_scaling_pair = (0.5,3)
n_lights = 20

note_old = []
light_dict = {0:n_lights}#,1:30,2:40}

#get dmx devices from user input
print("dmx port = ")
dmx_port = user_dmx()

#dmx_port = pysimpledmx.DMXConnection("COM11")

# set some big coloured lights
# set_big_light(dmx_port, n_lights + 1, (255,255,255))
# set_big_light(dmx_port, n_lights + 4, (0,255,0))
# set_big_light(dmx_port, n_lights + 7, (0,0,255))

lights = {}


for i in range(n_lights):
    lights[i] = {'root_dmx': i, 'func': set_light_bulb}



print("on")

# get midi devices from user input
port_dict = mt.user_midi()

envelope_params = {
    'type':'envelope', 
    'level':1, 
    'attack':0.1, 
    'decay':2, 
    'sustain':1, 
    'release':2,
    'lfo_level':0.2,
    'lfo_rate':1,
    'env_mode':"exponential"
}
cc_controls = {
    # 100: "lfo_rate",
    # 200: "lfo_level",
    # 300: "saturation",
    # 400: "hue",
    # 600: "level",
    # 700: "mode",
    
    1: "attack",
    2: "decay",
    4: "sustain",
    3: "release"}

instrument = inst.LightInstrument( 
    #note_list=[48,37],#,38,39,44,45,46], 
    # note_list= list(lights.keys()),
    light_list= list(lights.keys()), 
    cc_controls = cc_controls,
    envelope_params = envelope_params,
    mode = "cycle",
    max_length_attack = 5,  attack_exp_scaling_pair = 1.38, 
    max_length_release = max_length_decay,  decay_exp_scaling_pair = decay_exp_scaling_pair, 
    max_length_decay = max_length_decay,  release_exp_scaling_pair = decay_exp_scaling_pair )

instrument_beats = inst.LightInstrument( 
    #note_list=[48,37],#,38,39,44,45,46], 
    # note_list= list(lights.keys()),
    note_channel = 2,
    light_list= list(lights.keys()), 
    cc_controls = cc_controls,
    envelope_params = envelope_params,
    mode = "cycle" )

for i, light in instrument.light_envs.items():
    light.env.lfo_rate = random.uniform(1, 4)


modes_ind = 1

instrument_rack = [instrument]

osc_val = 0.5

easter_egg = False

while 1:


    for device, midi_port in port_dict.items():

        # if two cc messages with the same control and channel have come then only append most recent
        message_queue = mt.iter_pending_clean(midi_port)
            
        for msg in message_queue:
            
            print(msg)
            for inst in instrument_rack:
                inst.midi_action(msg)

    light_vals = instrument_rack[0].get_light_output()
    
    for light_key, light in lights.items():
        val = light_vals[light_key] # [ light_vals2[light_key][i] + light_vals[light_key][i] for i in range(3)] 
        
        #val = [col/max_val for col in val]
        light['func'](dmx_port, light['root_dmx'], val)
    
    if not easter_egg:
        time_val = time.time()
        sin_osc = ( (1- osc_val ) + osc_val * math.sin(time_val))
        sin_rot_osc = (1- osc_val ) + osc_val * math.sin(time_val+ math.pi *2 / 3)
        sin_rot_osc2 = (1- osc_val ) + osc_val * math.sin(time_val+ math.pi *4 / 3)
        set_big_light(dmx_port, n_lights + 1, ( sin_osc * 1, sin_rot_osc * 1, sin_osc * 1))
        set_big_light(dmx_port, n_lights + 4, ( sin_rot_osc * 1, sin_rot_osc * 1, sin_rot_osc * 0))
        set_big_light(dmx_port, n_lights + 7, ( sin_rot_osc2 * 1, sin_rot_osc2 * 0,sin_rot_osc2 * 1))

    if isinstance(dmx_port, DMXConnection):
        dmx_port.render()