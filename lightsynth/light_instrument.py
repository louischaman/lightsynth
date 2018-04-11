import light_function as lf
from copy import deepcopy
import colorsys

class LightEffects():
    '''
    Class for strobes and other effect lighting
    non-rgb

    '''

    def __init__(self, switch_notes=[60], cc_controls={}, light_type="strobe", note_channel = range(16)):
        self.switch_notes = switch_notes
        self.cc_controls = cc_controls
        self.type = light_type
        self.light_on = False
        self.note_channel = note_channel

        self.rate = 0.5
        self.brightness = 0.5
    
    def in_note_channel(self, midi_channel):
        # checks whether midi_channel from note is accepted by instruments channesl
        # works for instrument channel being a list or int
        if type(self.note_channel) is int:
            return(midi_channel == self.note_channel)
        if type(self.note_channel) is list:
            return(midi_channel in self.note_channel)
    
    def midi_action(self, midi_action):

        # is it the right channel
        if not self.in_note_channel(midi_action.channel):
            return

        if midi_action.type == "note_on" or  midi_action.type == "note_off":
            if midi_action.note in self.switch_notes:
                self.note_action(midi_action)

        elif midi_action.type == "control_change":
            self.cc_action(midi_action)

    def cc_action(self, cc_action):
        value = float(cc_action.value)/127
        if cc_action.control in self.cc_controls.keys():
            param =  self.cc_controls[cc_action.control]

            if param == "rate":
                self.rate = value
            
            if param == "brightness":
                self.brightness = value
            


    def note_action(self, note):
        if note.type == "note_on":
            self.light_on = not self.light_on



class LightInstrument():
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
            - effected by velocity

        - color (hue and saturation) either:
            - single color 
            - changing based on (note number, velocity, pattern)

        - brightness
            - all the same 
            - effected by velocity

        - which lights turn on when note plays
            - either fixed
            - changing based (note number, velocity, pattern)
    '''

    def __init__(
        self, light_list, 
        note_list = range(128), 
        rgb=(1, 0, 0), 
        envelope_params=None, 
        mode="cycle", 
        cc_controls = {}, 
        note_channel = range(16)
    ):
        """
        cc_controls are in the form {cc_index: param}

        """
        self.note_list = note_list
        self.light_list = light_list
        self.set_hsv_colour_rgb(rgb)
        self.set_mode(mode)
        self.light_envs = {}
        self.cc_controls = cc_controls
        self.note_channel = note_channel

        if not envelope_params:
            envelope_params = {
                'type':'envelope', 
                'level':1, 
                'attack':0, 
                'decay':0.01, 
                'sustain':0.9, 
                'release':0.1
            }

        self.env = lf.MidiLightAction(action_data = envelope_params) 
        self.note_envelopes = dict()
        for light in self.light_list:
            self.light_envs[light] = deepcopy(self.env)
        
     
    def set_mode(self, mode):
        self.mode = mode
        self.modes = ['all', 'single', 'cycle']
        self.mode_int = self.modes.index(self.mode)
        
        if mode == "cycle":
            self.light_counter = 0
            self.which_light = dict()

        if mode == "single":
            if len(self.note_list) != len(self.light_list):
                raise(ValueError("note must have same number as lights", self.note_list, self.light_list ))
            self.note_light = dict(zip(self.note_list, self.light_list))
        

    def add_notes(self, new_notes):
        self.note_list = self.note_list + new_notes

    def adjust_light_params(self):
        pass

    def get_rgb_colour(self):
        rgb = colorsys.hsv_to_rgb(self.hue, self.saturation, self.value)
        return rgb

    def set_hue(self, hue):
        self.hue = hue
    
    def set_saturation(self, saturation):
        self.saturation = saturation

    def set_value(self, value):
        self.value = value

    def set_hsv_colour_rgb(self, rgb):
        hsv = colorsys.rgb_to_hsv(*rgb)
        self.hue = hsv[0]
        self.saturation = hsv[1]
        self.value = hsv[2]

    def set_ADSR(self, parameter, value):
        pass

    def in_note_channel(self, midi_channel):
        # checks whether midi_channel from note is accepted by instruments channesl
        # works for instrument channel being a list or int
        if type(self.note_channel) is int:
            return(midi_channel == self.note_channel)
        if type(self.note_channel) is list:
            return(midi_channel in self.note_channel)

    def midi_action(self, midi_action):

        # is it the right channel
        if not self.in_note_channel(midi_action.channel):
            
            return

        if midi_action.type == "note_on" or  midi_action.type == "note_off":
            self.note_action(midi_action)

        if midi_action.type == "control_change":
            self.cc_action(midi_action)

    def cc_action(self, cc_action):
        value = float(cc_action.value)/127
        if cc_action.control in self.cc_controls.keys():
            param =  self.cc_controls[cc_action.control]

            if param == "level":
                self.set_value(value)
            
            if param in lf.param_list:
                print(param, value)
                for light, env in self.light_envs.iteritems():
                    env.set_attribute_01(param, value)
            
            if param == 'hue':
                print(param, value)
                self.set_hue(value)
            
            if param == 'saturation':
                print(param, value)
                self.set_saturation(value)

            if param == 'mode':
                
                print(param, value)
                # mode selector is using encoder which is either 0 or 127
                
                if value == 1:
                    self.mode_int = self.mode_int -1 
                else:
                    self.mode_int = self.mode_int +1 
                self.mode_int = self.mode_int % len(self.modes)
                    
                mode = self.modes[self.mode_int]
                self.set_mode(mode)
                print(self.mode)

    def note_action(self, note):

        # is it the right note
        if not note.note in self.note_list:
            return

        if note.type == "note_on":
            self.note_on_action(note)
        elif note.type == "note_off":
            self.note_off_action(note)

    def note_on_action(self, note):

        if self.mode == "cycle":
            light = self.light_list[self.light_counter]
            self.light_envs[light].note_on()
            # store note that turned the light on for turning off
            note_str = note.channel + note.note
            self.which_light[note_str] = light 
            self.light_counter = self.light_counter + 1
            self.light_counter = self.light_counter % len(self.light_list)

        if self.mode == "all":
            for light, env in self.light_envs.iteritems():
                self.light_envs[light].note_on()

        if self.mode == "single":
            light = self.note_light[note.note]
            self.light_envs[light].note_on()


    def note_off_action(self, note):
        
        if self.mode == "cycle":
            note_str = note.channel + note.note 
            if note_str in self.which_light.keys():
                light = self.which_light[note_str]
                self.light_envs[light].note_off()
        
        if self.mode == "all":
            for light, env in self.light_envs.iteritems():
                self.light_envs[light].note_off()

        if self.mode == "single":
            light = self.note_light[note.note]
            self.light_envs[light].note_off()

    def get_light_output(self):
        output_list = {}
        rgb = self.get_rgb_colour()
        for light, env in self.light_envs.iteritems():
            rgb_output = [colour * env.update() for colour in rgb]
            output_list[light] = rgb_output
        
        return(output_list)





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
