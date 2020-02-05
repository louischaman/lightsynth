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
from lightsynth import controllers as ctls

import utils.configuration as conf
import utils.dmxtools as dt
import utils.miditools as mt
from devices import Bulb, Par3RGB
from pysimpledmx import DMXConnection
from utils.maths import sign
from utils.message import msg_generic as gmsg

import collections

demo_mode = True
unlock_sequence = [66, 68, 66, 64, 66]


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
    port_dict_out = mt.user_midi_output(1)

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
        mode="one_to_one")
    
    activate_msg = gmsg(type = 'swith_out')
    toggle_out = gmsg(type = 'toggle_device')

    print(activate_msg)
    def switch_output_channel(midi_out_dev, msg):
        midi_out_dev.switch_channel( (midi_out_dev.set_channel + 1) % 2)

    def toggle_out_action(midi_out_dev, msg):
        midi_out_dev.toggle_out()

    generated_msgs = collections.deque()
    activate_sequence = [
        (0,toggle_out),
    ] + [
        (i/64, mido.Message('control_change', control = 7, value = int(i*2.25) % 128))
        for i in range(128)
    ] + [
        (1-0.001,mido.Message('note_off', channel = 0, note = 45 ) ),
        (1,toggle_out),
        (1, activate_msg),
        (1,mido.Message('note_on',channel = 12,note = 82)),
        (1,mido.Message('note_on',channel = 12,note = 70)),
        (1.001,mido.Message('note_off',channel = 12,note = 82)),
        (1.001,mido.Message('note_off',channel = 12,note = 70)),
    ]

    unlocker = ctls.noteUnlocker(
        msg_queue=generated_msgs, 
        seq=unlock_sequence, 
        activate_msgs_sequence=activate_sequence,
        channel=2
    )
    out_dev = list(port_dict_out.values())[0]
    midi_output = mt.midiOutputDevice(out_dev, set_channel=1)

    note_diff_fn = lambda note_diff: int( min(abs(note_diff),2) * sign(note_diff) )
    instrument.set_mode("follow", {'note_diff_fn':note_diff_fn})

    effectRGB = li.EffectColourise()

    switch_channel_action = rt.action_mapping(
        action = switch_output_channel, 
        filter_params = {'type':'swith_out'}
    )
    toggle_device_action = rt.action_mapping(
        action = lambda x,y: x.toggle_device(),
        filter_params={'type': 'toggle_device'}
    )
    cc_map = [
        rt.cc_action(control=1, param="attack" , scaling_fn='def_exp'),
        rt.cc_action(control=2, param="decay" , scaling_fn='def_exp'),
        rt.cc_action(control=4, param="sustain" , scaling_fn='def_exp'),
        rt.cc_action(control=5, param="release" , scaling_fn='def_exp'),
    ]

    cc_colour_mapping = [
        rt.cc_action(control=7, param="hue" ),
        rt.cc_action(control=8, param="saturation" ),
    ]
    
    example_mapping = [
        rt.deviceMap(
            device = unlocker,
            action_mappings = [
                rt.pass_notes_action({'channel':0}),
                toggle_device_action,
            ]
        ),
        rt.deviceMap(
            device = instrument,
            action_mappings = cc_map + [rt.pass_notes_action()],
            filter_params = {'channel':0},
            ),
        rt.deviceMap(
            device = instrument2,
            action_mappings = cc_map + [rt.pass_notes_action()],
            filter_params = {'channel':2},
        ),
        rt.deviceMap(
            device = midi_output,
            action_mappings = [
                rt.pass_all_action({'channel':0}),
                switch_channel_action,
                toggle_device_action
            ]
        ),
        rt.deviceMap(
            device = mt.midiOutputDevice(out_dev),
            action_mappings = [
                rt.pass_all_action({'channel':12})
            ]
        ),
        rt.deviceMap(
            device = effectRGB,
            action_mappings = cc_colour_mapping
        ),
    ]

    mr = rt.midiRouterLI(device_mapping = example_mapping)

    while 1:
        for _, midi_port in port_dict.items():

            # if two cc messages with the same control and channel have come then only append most recent
            input_msg_list = list(midi_port.iter_pending())
            generated_msgs_list = [generated_msgs.popleft() for _i in range(len(generated_msgs))]

            message_queue = list(mt.iter_pending_clean(input_msg_list + generated_msgs_list))

            for msg in message_queue:
                print(msg)
                # msg = rt.msg_constructor(test = 'a')
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
