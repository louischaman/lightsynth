from .list_ports import serial_ports
from pprint import pprint
from pysimpledmx import DMXConnection
import numpy as np

import argparse
from pythonosc import osc_message_builder
from pythonosc import udp_client
import math

max_scaling = 0.4
def exp_scaling_fn(exp_rate, value_0_1):
    # scales from 0 to max_val exponentially so more control in low end
    return  ( math.pow(exp_rate, value_0_1) - 1 ) /(exp_rate - 1)


# class light_rack:
#     def __init__(self, lights):
#         self.lights = lights
    


#     def show_lights(self, pattern, dmx_port):
#         np.matrix(pattern)



def set_dmx(dmx_port, channel, level, exp_scaling= 1.7):
    
    if type(dmx_port) is dict:
        if channel in dmx_port.keys():
            #rescale to 0-1
            if dmx_port[channel] != level:
                dmx_port[channel] = level
                show_dmx(dmx_port)
        else:
            dmx_port[channel] = level
            show_dmx(dmx_port)
        return
    else:
        
        if exp_scaling:
            level = exp_scaling_fn(exp_scaling, level)

        level = level*255
        # doesnt go above 255 or below 0
        level = min(level,255)
        level = max(level,0)

        try:
            dmx_port.setChannel(channel, int(level * max_scaling) ) 
        #   dmx_port.render()
        except Exception as error:
            print(channel, level)
            raise(error)

def show_dmx(dmx_port):
    if type(dmx_port) is dict:
        print( " ".join('%0.2f' % item for item in dmx_port.values()) )
        
def set_light_cheap(dmx_port, light_channel, rgb):
    # set position one (level) to max
    set_dmx(dmx_port, light_channel, 255)

    for i, col_lev in enumerate(rgb):
        set_dmx(dmx_port, light_channel + i + 1, col_lev )


def set_effect(dmx_port, light_channel, values):
    # set position one (level) to max

    for i, col_lev in enumerate(values):
        set_dmx(dmx_port, light_channel + i, col_lev )
         

def set_light_bulb(dmx_port, light_channel, rgb):
    # set red to lightbulb
    set_dmx(dmx_port, light_channel + 1, rgb[0] )

def set_big_light(dmx_port, light_channel, rgb):
    # set position one (level) to max

    for i, col_lev in enumerate(rgb):
        set_dmx(dmx_port, light_channel + i, col_lev )

class OSCDMXSender:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default="127.0.0.1",
            help="The ip of the OSC server")
        parser.add_argument("--port", type=int, default=12000,
            help="The port the OSC server is listening on")
        args = parser.parse_args()
        self.client = udp_client.SimpleUDPClient(args.ip, args.port)

    def setChannel(self, channel, level ):
        self.client.send_message("/dmx",(channel-1,level))

def user_dmx():
    #get dmx devices from user input
    available_ports = serial_ports()
    if len(available_ports ) > 0:
        pprint([ (i, available_ports[i]) for i in range(len(available_ports))] )
        which_port = int(input('select port number: '))
        
        dmx_port = DMXConnection(available_ports[which_port])
    else:
        print("no_dmx")
        dmx_port = OSCDMXSender()
    return(dmx_port)