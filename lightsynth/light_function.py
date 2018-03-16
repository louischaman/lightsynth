import math
import time
from adsr import ADSRenvelope as env
action_type_lookup = {"switching":"s", "gate":"g", "envelope":"e"}

class MidiLightAction:
    '''
    This class has all the information for a type of action 

    It currently contains the action types

    1. midi on and off with light on and off
    2. gate with a timer

    This class contains functions:
        note_on
        note_off
        set_dmx
    '''

    def __init__(self, action_data):
        
        self.action_data = action_data
        self.action_type = action_data['type']

        if self.action_type == "switching":
            self.level = action_data['level']
            self.note_is_on = False

        elif self.action_type == "gate":
            self.level = action_data['level']
            self.start_time = time.time()
            self.gate_length = action_data['gate_length'] # time in seconds to stay on for
            self.note_is_on = False

        elif self.action_type == "envelope":
            self.level = action_data['level']
            self.start_time = time.time()
            self.env = env(action_data['attack'], 
                           action_data['decay'], 
                           action_data['sustain'], 
                           action_data['release'])

        else:
            raise(ValueError("type not recognised"))

    def midi_message(self, msg):
        if msg.type == "note_on":
            return self.note_on()
        elif msg.type == "note_off":
            return self.note_off()
        else:
            return None

    def set_attribute(self, attribute, value):
        if attribute in ['attack', 'decay', 'sustain', 'release']:
            setattr(self.env, attribute, value)
        else:
            setattr(self, attribute, value)


    def set_attribute_01(self, attribute, value):
        '''
        sets attribute with value a float from 0 to 1
        '''
        value = min(max(value,0),1)
        
        if attribute in ['attack', 'decay', 'release']:
            max_val = 5
            exp_rate = 5
            val_exp = max_val * ( math.pow(exp_rate, value) - 1 ) /(exp_rate - 1)
            setattr(self.env, attribute, val_exp)
        elif attribute in ['decay-release']:
            setattr(self.env, 'decay', value)
            setattr(self.env, 'release', value)
        elif attribute in ['smoothness']:
            setattr(self.env, 'attack', value)
            setattr(self.env, 'release', value)
            setattr(self.env, 'decay', value + 0.07)
            setattr(self.env, 'sustain', value-0.1)
            
        elif attribute in ['sustain']:
            setattr(self.env, attribute, value)
        elif attribute in ['gate_length']:
            setattr(self, attribute, value)
        elif attribute in ['level']:
            setattr(self, attribute, value)
        else:
            raise(KeyError('attribute %s not recognised' % (attribute)))

    def note_on(self):
        self.note_is_on = True
        if self.action_type == "switching":
            return self.level
        elif self.action_type == "gate":
            self.start_time = time.time()
            return self.level
        elif self.action_type == "envelope":
            self.env.on_note()


    def note_off(self):
        if self.action_type == "switching":
            self.note_is_on = False
        elif self.action_type == "gate":
            return None
        elif self.action_type == "envelope":
            self.env.off_note()
    
    def update(self):
        if self.action_type == "switching":
            return self.note_is_on * self.level

        elif self.action_type == "gate":
            if self.note_is_on & ( time.time() - self.start_time > self.gate_length ) :
                self.note_is_on = False
                return 0
            else:
                return self.note_is_on * self.level

        elif self.action_type == "envelope":
            return self.env.get_level() * self.level

    def get_status(self):
        if self.action_type == "switching":
            return "note on is " + str(self.note_is_on)
        elif self.action_type == "gate":
            return "note on is " + str(self.note_is_on)

        elif self.action_type == "envelope":
            return "note status is " + self.env.get_phase()


    def __repr__(self):
        return "<Act-%s>" % (action_type_lookup[self.action_type])