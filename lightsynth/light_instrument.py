import light_function as lf
from copy import deepcopy

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

    def __init__(self, note_list, light_list, rgb=(1, 0, 0), envelope_params=None, mode="cycle"):
        self.note_list = note_list
        self.light_list = light_list
        self.set_rgb_colour(rgb)
        self.mode = mode
        self.light_envs = {}

        if not envelope_params:
            envelope_params = {
                'type':'envelope', 
                'level':255, 
                'attack':0, 
                'decay':0.01, 
                'sustain':0.9, 
                'release':0.1
            }
        self.env = lf.MidiLightAction(action_data = envelope_params) 
        self.note_envelopes = dict()
        for light in self.light_list:
            self.light_envs[light] = deepcopy(self.env)
        
        if mode == "cycle":
            self.light_counter = 0
            self.which_light = dict()

    def add_notes(self, new_notes):
        self.note_list = self.note_list + new_notes

    def adjust_light_params(self):
        pass

    def set_hsv_colour(self, hue, saturation):
        pass

    def set_rgb_colour(self, rgb):
        max_val = max(rgb)
        self.rgb = tuple([float(x)/max_val for x in rgb])

    def set_brightness(self, level):
        pass

    def set_ADSR(self, parameter, value):
        pass

    def note_action(self, note):
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


    def note_off_action(self, note):
        
        if self.mode == "cycle":
            note_str = note.channel + note.note 
            if note_str in self.which_light.keys():
                light = self.which_light[note_str]
                self.light_envs[light].note_off()
        
        if self.mode == "all":
            for light, env in self.light_envs.iteritems():
                self.light_envs[light].note_off()

    def get_light_output(self):
        output_list = {}
        for light, env in self.light_envs.iteritems():
            rgb_output = [colour * env.update() for colour in self.rgb]
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
