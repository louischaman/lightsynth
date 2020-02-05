from . import adsr
from copy import deepcopy
import colorsys
import time
from .light_effects import delay_single
from .light_switch import LightSwitch
import utils.miditools as mt
import utils.maths as maths

class EnvArray():
    ''' envelope array with on and off for each element
    '''
    def __init__(self, n_envs, attack, decay, sustain, release):
        self.envs = [adsr.ADSRenvelope(attack,decay,sustain,release) for i in range(n_envs)]

    def set_adsr_param(self, param, value):
        for env in self.envs:
            setattr(env, param, value) 

    def note_on(self, which_env):
        self.envs[which_env].on_note()

    def note_off(self, which_env):
        self.envs[which_env].off_note()

    def get_values(self):
        return [env.get_level() for env in self.envs]


class LightInstrumentGS(mt.simpleMidiDevice):
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

        - which lights turn on when note plays
            - either fixed
            - changing based (note number, velocity, pattern)
    '''

    def __init__(
        self, n_lights, 
        envelope_params=None, 
        mode="cycle",
        mode_params=None,
        cc_mapping = None
    ):
        """
        cc_mapping are in the form {cc_index: param}
        """
        super().__init__()

        if envelope_params is None:
            envelope_params = {
                'attack':0, 
                'decay': 0.2, 
                'sustain':0.9, 
                'release':0.3
            }

        if mode_params is None:
            mode_params = {}

        self.set_mode(mode, mode_params)
        
        self.cc_mapping = cc_mapping # maybe take out cc mapping since router means we don't need it

        self.env_array = EnvArray(n_lights, **envelope_params)
        self.n_lights = n_lights

        # note_light is mapping from midi note to light num 
        # for turning off the right light
        self.note_light = {}

        self.last_light = -1

        self.note_buffer = mt.noteBuffer(2)
    
    def set_mode(self, mode, mode_params):
        self.mode = mode
        if mode == 'follow':
            note_diff_fn = lambda note_diff:min(abs(note_diff),1) * maths.sign(note_diff)
            self.note_diff_fn = mode_params.get('note_diff_fn', note_diff_fn)

    def set_param(self, parameter, value):
        print(parameter, value)
        self.env_array.set_adsr_param(parameter, value)

    def note_on_to_light_mapping(self, note):
        # gets the light to turn on for incoming note
        if self.mode == 'one_to_one':
            return (note) % self.n_lights
        
        if self.mode == 'cycle':
            self.last_light = (self.last_light + 1) % self.n_lights
            return self.last_light
        
        if self.mode == 'follow':
            last_note = self.note_buffer.get_last(2)[0]
            note_diff =  note - last_note
            note_diff_transform = self.note_diff_fn(note_diff)
            self.last_light = (self.last_light + note_diff_transform) % self.n_lights
            return self.last_light

    def note_on_action(self, note, velocity):
        self.note_buffer.note_on_action(note, velocity)
        which_light = self.note_on_to_light_mapping(note)

        # if note is already on turn off
        if note in self.note_light:
            which_light_off = self.note_light[note]
            self.env_array.note_off(which_light_off)

        # store which note turned the light on
        self.note_light[note] = which_light
        self.env_array.note_on(which_light)


    def note_off_action(self, note):
        if note in self.note_light:
            which_light = self.note_light[note]
            self.env_array.note_off(which_light)
        
    def get_light_output(self):
        return self.env_array.get_values()
        
    def cc_action(self, control, value):
        self.set_param(self.cc_mapping[control], value/127)


class EffectColourise:
    def __init__(self, hue=1, saturation=1):
        self.hue = hue
        self.saturation = saturation

    def effect(self, light_vals):
        out_vals = []
        for val in light_vals:
            rgb = colorsys.hsv_to_rgb(self.hue, self.saturation, val)
            out_vals.append(rgb)
        return out_vals
    
    def set_param(self, parameter, value):
        print(parameter, value)
        if parameter in ['hue', 'saturation']:
            setattr(self, parameter, value)
        else:
            raise ValueError('parameter value not hue or saturation')