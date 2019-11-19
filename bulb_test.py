import argparse
import copy
import math
import random
import struct
import time
from pprint import pprint

import mido

from lightsynth import router as rt
from lightsynth import light_instrument as li

import utils.configuration as conf
import utils.dmxtools as dt
import utils.miditools as mt
from devices import Bulb, Par3RGB
from pysimpledmx import DMXConnection
from utils.maths import sign

demo_mode = True


def main(lights_file):
    # get dmx devices from user input
    print("dmx port = ")
    dmx_port = dt.user_dmx(demo_mode)

    # get lights from file
    lights = conf.load_lights(lights_file)
    for light in lights:
        light.dmx_port = dmx_port

    lights_bulbs = [light for light in lights if isinstance(light, Bulb)]
    lights_rgbs = [light for light in lights if isinstance(light, Par3RGB)]
    print(f'Found {len(lights_bulbs)} Bulbs and {len(lights_rgbs)} Par3RGBs')

    print("on")

    # get midi devices from user input
    port_dict = mt.user_midi(0)

    envelope_params = {
        'attack': 0.1,
        'decay': 2,
        'sustain': 1,
        'release': 2,
    }

    instrument = li.LightInstrumentGS(
        n_lights=len(lights_bulbs),
        envelope_params=envelope_params,
        mode="follow")

    instrument2 = li.LightInstrumentGS(
        n_lights=len(lights_rgbs),
        envelope_params=envelope_params,
        mode="follow")

    note_diff_fn = lambda note_diff: int( min(abs(note_diff),2) * sign(note_diff) )
    instrument.set_mode("follow", {'note_diff_fn':note_diff_fn})

    effectRGB = li.EffectColourise()

    cc_mapping = {
        1: {'param':"attack" , 'scaling_fn': 'def_exp'},
        2: {'param':"decay" , 'scaling_fn': 'def_exp'},
        4: {'param':"sustain" , 'scaling_fn': 'def_exp'},
        5: {'param':"release" , 'scaling_fn': 'def_exp'},
    }

    cc_colour_mapping = {
        7: "hue",
        8: "saturation",
    }
    example_mapping = [
        {
            'device': instrument,
            'type': 'midi',
            'cc': {
                'cc_mapping': cc_mapping
            }
        },
        {
            'device': instrument2,
            'type': 'midi',
            'note':{
                'note_range': list(range(70,80))
            },
            'cc': {
                'cc_mapping': cc_mapping
            }
        },
        {
            'device': effectRGB,
            'type': 'effect',
            'cc': {
                'cc_mapping': cc_colour_mapping
            }
        }     
    ]

    mr = rt.midiRouterLI(mapping = example_mapping)
    import code; code.interact(local=dict(globals(), **locals()))

    while 1:

        for _, midi_port in port_dict.items():

            # if two cc messages with the same control and channel have come then only append most recent
            message_queue = mt.iter_pending_clean(midi_port)

            for msg in message_queue:
                print(msg)
                mr.on_msg(msg)

        light_vals = instrument.get_light_output()
        rgb_vals = effectRGB.effect(instrument2.get_light_output())
        
        for light, values in zip(lights_bulbs, light_vals):
            light.values = [values]
            light.dmx_update()

        for light, rgb_val in zip(lights_rgbs, rgb_vals):
            light.values = rgb_val
            light.dmx_update()
        if isinstance(dmx_port, DMXConnection):
            dmx_port.render()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Send MIDI to light instruments and route the output to lights over DMX')
    parser.add_argument('--lightfile', type=str, help='Path to a light setup YAML file',
                        default='vlight/demo/lights_grid.yaml')

    args = parser.parse_args()
    main(args.lightfile)
