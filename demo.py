import mido
import lightsynth.light_instrument as inst
import pysimpledmx
import utils.miditools as mt
from utils.dmxtools import * 
from collections import OrderedDict

from pprint import pprint

note_old = []
light_dict = {0:20,1:30,2:40}

#get dmx devices from user input
dmx_port = user_dmx()

#dmx_port = pysimpledmx.DMXConnection("COM11")

set_dmx(dmx_port, 1, 255)
set_dmx(dmx_port, 2, 255)

set_light_cheap(dmx_port, 20, (255,0,0))
set_light_cheap(dmx_port, 30, (255,0,0))
set_light_cheap(dmx_port, 40, (255,0,0))

print("on")

# get midi devices from user input
midi_devices = mido.get_input_names()
port_dict = mt.user_midi()

envelope_params = {
    'type':'envelope', 
    'level':255, 
    'attack':0, 
    'decay':1, 
    'sustain':0, 
    'release':0.2
}

instrument = inst.LightInstrument( note_list=range(126), light_list=light_dict.keys() )
instrument2 = inst.LightInstrument( note_list=range(126), light_list=light_dict.keys(), 
    mode="all", rgb=(1,1,1), envelope_params = envelope_params )

while 1:
    for device, midi_port in port_dict.iteritems():

        # if two cc messages with the same control and channel have come then only append most recent
        message_queue = mt.iter_pending_clean(midi_port)
            
        for msg in message_queue:
            print(msg)
            if(msg.type == "control_change"):
                pass

            elif(msg.type == "note_on" or msg.type == "note_off"):
                if msg.channel == 1:
                    instrument.note_action(msg)
                if msg.channel == 0:
                    instrument2.note_action(msg)

            
    light_vals = instrument.get_light_output()
    light_vals2 = instrument2.get_light_output()
    for light, channel in light_dict.iteritems():
        val = [ light_vals2[light][i] + light_vals[light][i] for i in range(3)] 
        set_light_cheap(dmx_port, channel, val)