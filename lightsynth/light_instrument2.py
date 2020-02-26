from . import adsr
from copy import deepcopy
import colorsys
import time
from .light_effects import LightEffects
from .light_switch import LightSwitch

class EnvArray():
    ''' envelope array with on and off for each element
    '''
    def __init__(self, n_envs, attack, decay, sustain, release):
        self.envs = [adsr.ADSRenvelope(attack,decay,sustain,release) for i in range(n_envs)]

    def set_adsr_param(self, param, value):
        for env in self.envs:
            setattr(env, param, value) 

    def note_on(self, which_env):
        self.envs[which_env].note_on()

    def note_off(self, which_env):
        self.envs[which_env].note_off()

    def get_values(self):
        return [env.get_level() for env in self.envs]


class LightInstrumentCycleGS():
    '''
    setup with
    - light list (total list)
    - note list  (all notes that trigger the visual action)

    One or more notes are mapped to a single visual action 
    parameters effect all visual action

    outputs an object that is combined with other light instruments to determine final output

    on a note either:
        - trigger the light with the parameters defined below
        - activate a special mode eg strobe

    Parameters include:
        - ADSR control either:
            - all the same 
            - affected by velocity
            
        - brightness
            - all the same 
            - affected by velocity

        - which lights turn on when note plays
            - either fixed
            - changing based (note number, velocity, pattern)
    '''

    def __init__(
        self, n_lights, 
        envelope_params=None, 
        mode="cycle", 
        cc_controls = {}
    ):
        """
        cc_controls are in the form {cc_index: param}

        """
        self.cc_controls = cc_controls

        if not envelope_params:
            envelope_params = {
                'type':'envelope', 
                'level':1, 
                'attack':0, 
                'decay':0.01, 
                'sustain':0.9, 
                'release':0.1
            }

        self.env_array = EnvArray(n_lights)
        self.n_lights = n_lights

        # light_list is mapping from midi note to light num
        self.light_list = {}

    def set_ADSR(self, parameter, value):
        print(parameter, value)
        self.env_array.set_adsr_param(param, value)

    def on_msg(self, msg):
        if midi_action.type == "note_on" :
            self.note_on_action(msg)
        
        elif midi_action.type == "note_off":
            self.note_action(msg)

        elif midi_action.type == "control_change":
            self.cc_action(msg)

    def note_on_to_light_mapping(note):
        

    def note_on_action(self, msg):




        light = self.light_list[self.light_counter]
        self.env_array.note_on(msg.note)
        # store note that turned the light on for turning off
        note_str = str(msg.note)
        self.which_light[note_str] = light 
        self.light_counter = self.light_counter + 1
        self.light_counter = self.light_counter % len(self.light_list)

    def note_off_action(self, note):
        note_str = str(msg.note)
        if note_str in self.which_light.keys():
            light = self.which_light[note_str]
            self.env_array.note_off(light)
        
    def get_light_output(self):
        return self.env_array.get_values()




# class NoteAction:
#     def __init__(self, light_list, selector_data):


#     def set_action(self, selector_data):
#     '''
#     selector_data has format {"type": "type_string", "paramters": parameters_object}

#     type includes
#         - cycle - with parameters being the light order for cycle [1, 2, 3, [4, 5]]
#         - velocity scaling - order where more lights are triggered for each step in velocity
#         - velocity selecting - different lights are triggered by different velocities
#     '''
#         if selector_data['type'] = "cycle":
#             counter = 0

#     def cycle(self, note):


#     def on_note():
