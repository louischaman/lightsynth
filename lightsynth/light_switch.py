class LightSwitch():
    '''
    class to switch lights on and off
    '''
    def __init__(self, switch_notes, on_notes, note_channel):
        self.switch_notes = switch_notes
        self.on_notes = on_notes
        self.note_channel = note_channel
        self.light_on = False

    def note_action(self, note):
        if note.note in self.on_notes:
            if note.type == "note_on" :
                self.light_on = True
            elif note.type == "note_off":
                self.light_on = False
        
        if note.note in self.switch_notes:
            if note.type == "note_on":
                self.light_on = not self.light_on
        

    def midi_action(self, midi_action):

        # is it the right channel
        if not self.in_note_channel(midi_action.channel):
            return

        if midi_action.type == "note_on" or  midi_action.type == "note_off":
            self.note_action(midi_action)

        elif midi_action.type == "control_change":
            return
    
    def in_note_channel(self, midi_channel):
        # checks whether midi_channel from note is accepted by instruments channesl
        # works for instrument channel being a list or int
        if type(self.note_channel) is int:
            return(midi_channel == self.note_channel)
        if type(self.note_channel) is list:
            return(midi_channel in self.note_channel)
    
    def get_light_output(self):
        return([self.light_on])