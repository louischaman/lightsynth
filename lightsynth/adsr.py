import time
import math     

class ADSRenvelope(object):
    '''
    this class does the 
        Attack
        Decay
        Sustain
        Release 
    based on time since note on event

    max attack is always 1
    '''
    def __init__(self, attack, decay, sustain, release, lfo_level=0, lfo_rate=1,  mode="linear", level=1):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.mode = mode
        self.note_on = False
        self.event_time = 0
        self.level = level

    def on_note(self):
        '''
        on a note on signal run this
        '''
        note_level = self.get_level()
        time_since_event = note_level * self.attack

        # so that the attack doesnt start from 0 if part way through a cycle
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
    

    def exp_scaling(self, exp_rate, value_0_1):
        # scales from 0 to 1 exponentially so more control in low end
        return ( math.pow(exp_rate, value_0_1) - 1 ) /(exp_rate - 1)

    def get_attack_level(self, time_since_event):
        return (1.0 /self.attack * time_since_event)

    
    def get_decay_level(self, time_since_event):
        decay_time = time_since_event  - self.attack
        m = float(self.sustain - 1) / self.decay
        c = 1
        return m * decay_time + c
    
    def get_release_level(self, time_since_event):
        if self.mode == "linear":
            return (1 - 1.0 / self.release * time_since_event) * self.off_level
        if self.mode == "exponential":
            return self.exp_scaling( 2, (1 - 1.0 / self.release * time_since_event) * self.off_level)

    def get_level(self):
        '''
        gets the level of the envelope at any time
        '''
        time_since_event = time.time() - self.event_time
        phase = self.get_phase()
        if phase == "attack":
            level = self.get_attack_level(time_since_event)
        if phase == "decay":
            level = self.get_decay_level(time_since_event)
        if phase == "sustain":
            level = self.sustain
        if phase == "release":
            level = self.get_release_level(time_since_event)
        if phase == "off":
            level = 0

        return level * self.level

    def debug_env(self):
        print("level %f - time %f - phase %s" % (self.get_level(), time.time() - self.event_time, self.get_phase() ) )