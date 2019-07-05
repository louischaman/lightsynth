from . import light_function as lf
from copy import deepcopy
import colorsys
import time

class LightEffects():
    '''
    Class for strobes and other effect lighting
    non-rgb

    for triggering the martin note_time is established
    for this a pulse is sent
    while pulse is high note_time is true
                

    '''

    def __init__(self, on_notes=[42], trigger_note = [43], switch_notes=[60], cc_controls={}, light_type="PS", note_channel = list(range(16)) ):

        # switch notes only have on actions for latching
        self.switch_notes = switch_notes

        # on notes have on and off action
        self.on_notes = on_notes

        # on notes are on for a bit
        self.trigger_note = trigger_note

        self.cc_controls = cc_controls
        self.light_type = light_type
        self.light_on = False
        self.note_channel = note_channel

        self.rate = 0.5
        self.brightness = 0.5
        self.duration = 0
        self.effect = 0
        self.strobe_length = 0.05
        self.time_on = 0
        self.is_note_time = False

    
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

        elif midi_action.type == "control_change":
            self.cc_action(midi_action)

    def note_action(self, note):
        
        if note.type == "note_on":
            if note.note in self.switch_notes:
                self.light_on = not self.light_on
                self.is_note_time = False

            if note.note in self.on_notes:
                self.light_on = True
                self.is_note_time = False
            
            if note.note in self.trigger_note:
                self.light_on = True
                self.time_on = time.time()
                self.is_note_time = True
                return

        if (note.type == "note_off") & (note.note in self.on_notes):
            self.light_on = False


    def cc_action(self, cc_action):
        value = float(cc_action.value)/127
        if cc_action.control in self.cc_controls.keys():
            print("ok")
            param =  self.cc_controls[cc_action.control]

            if param in ["rate", "brightness", "duration", "effect", "strobe_length"]:
                setattr(self, param, value)
                print(param, value)

    def get_light_output(self):
        output_list = {}

        if not self.light_on:
            return([0,0,0,0])

        elif self.is_note_time and time.time() > self.time_on + self.strobe_length:
            self.light_on = False
            return([0,0,0,0])

        elif self.light_type == "martin":
            if self.is_note_time:
                print([self.brightness, 0,0,0])
                return([self.brightness, 0,0,0])
            else:
                return([self.brightness, self.duration, self.rate, self.effect])

        elif self.light_type == "PS":
            return([self.rate, self.brightness])

        return(output_list)