import time

class ADSRenvelope:
    '''
    this class does the 
        Attack
        Decay
        Sustain
        Release 
    based on time since note on event
    '''
    def __init__(self, attack, decay, sustain, release, mode="linear"):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.mode = mode
        self.note_on = False
        self.event_time = 0

    def on_note(self):
        '''
        on a note on signal run this
        '''
        note_level = self.get_level()
        time_since_event = note_level * self.attack 

        self.event_time = time.time() - time_since_event
        self.note_on = True

    def off_note(self):
        '''
        on a note off signal run this
        '''
        self.off_level = self.get_level()
        self.event_time = time.time()
        self.note_on = False
        
    
    def get_phase(self):
        '''
        returns as a string what phase the ADSR envelope is in
        '''

        time_since_event = time.time() - self.event_time
        if self.note_on:
            if time_since_event < self.attack:
                return "attack"
            elif time_since_event > self.attack and time_since_event < (self.decay + self.attack):
                return "decay"
            else:
                return "sustain"
        else: # note_on is false
            if time_since_event < self.release:
                return "release"
            else:
                return "off"
    
    def get_attack_level(self, time_since_event):
        if self.mode == "linear":
            return (1.0 /self.attack * time_since_event)

    
    def get_decay_level(self, time_since_event):
        if self.mode == "linear":
            decay_time = time_since_event  - self.attack
            m = float(self.sustain - 1) / self.decay
            c = 1
            return m * decay_time + c
    
    def get_release_level(self, time_since_event):
        if self.mode == "linear":
            return (1 - 1.0 / self.release * time_since_event) * self.off_level
    
    def get_level(self):
        '''
        gets the level of the envelope at any time
        '''
        time_since_event = time.time() - self.event_time
        phase = self.get_phase()
        if phase == "attack":
            return self.get_attack_level(time_since_event)
        if phase == "decay":
            return self.get_decay_level(time_since_event)
        if phase == "sustain":
            return self.sustain
        if phase == "release":
            return self.get_release_level(time_since_event)
        if phase == "off":
            return 0

    def debug_env(self):
        print("level %f - time %f - phase %s" % (self.get_level(), time.time() - self.event_time, self.get_phase() ) )