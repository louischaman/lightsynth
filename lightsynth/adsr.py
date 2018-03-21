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
    def __init__(self, attack, decay, sustain, release, lfo_level=0, lfo_rate=1,  mode="linear"):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.mode = mode
        self.note_on = False
        self.event_time = 0
        self.lfo_level = lfo_level
        self.lfo_rate = lfo_rate

        # for lfo
        self.note_on_time =  time.time()
        self.extra_time = 0

    def on_note(self):
        '''
        on a note on signal run this
        '''
        note_level = self.get_level()
        time_since_event = note_level * self.attack

        # so that the attack doesnt start from 0 if part way through a cycle
        self.event_time = time.time() - time_since_event
        self.note_on = True

        # for lfo
        #self.note_on_time =  time.time()

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

    def get_level_adsr(self):
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

    def set_lfo_rate(self, rate):
        self.note_on_time  = time.time() - rate * ( (time.time() - self.note_on_time)  / self.lfo_rate )
        #self.extra_time = sin_time
        self.lfo_rate = max(rate, 0.00001)

    def get_level(self):
        level_pre_lfo = self.get_level_adsr()
        if self.lfo_level == 0:
            return level_pre_lfo

        else:
            sine_level = math.sin( (time.time() - self.note_on_time) * 2 * math.pi / self.lfo_rate) 
            osc_level = (sine_level + 1) * 0.5 * self.lfo_level
            
            return level_pre_lfo * (1 - self.lfo_level + osc_level)

    def debug_env(self):
        print("level %f - time %f - phase %s" % (self.get_level(), time.time() - self.event_time, self.get_phase() ) )