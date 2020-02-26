import utils.miditools as mt
import mido
from utils.message import msg_generic as gmsg
import time
from . import generator 

seq = list(range(40,48))

nbuf = mt.noteBuffer(len(seq))

class noteUnlocker:
    def __init__(self, msg_queue, seq, activate_msgs_sequence, channel=1, start_note=70):
        self.msg_queue = msg_queue
        self.seq = seq
        self.nbuf = mt.noteBuffer(len(seq))
        self.channel = channel
        self.start_note = start_note
        self.n_match_old = 0
        self.activate_msgs_sequence = activate_msgs_sequence
        self.device_active = True
    
    def on_msg(self, msg):
        if not self.device_active:
            return
        self.nbuf.on_msg(msg)
        n_match = self.nbuf.count_notes_match(self.seq)
        if not msg.type == 'note_on':
            return 
        print(n_match)
        if n_match>0 and n_match>=self.n_match_old:
            out_msg = mido.Message("note_on", note = self.start_note + n_match - 1, channel = self.channel )
            self.msg_queue.append(out_msg)
            if n_match == len(self.seq):
                print('activate')
                generator.appendMsgSequence(self.msg_queue,self.activate_msgs_sequence).start()
                # self.msg_queue.extend(self.activate_msgs)
        elif n_match>0:
            for i in range(len(self.seq)):
                out_msg = mido.Message("note_off", note = self.start_note + i, channel = self.channel )
                self.msg_queue.append(out_msg)
            for i in range(n_match):
                out_msg = mido.Message("note_on", note = self.start_note + i, channel = self.channel )
                self.msg_queue.append(out_msg)
        elif self.n_match_old !=0: 
            for i in range(len(self.seq)):
                out_msg = mido.Message("note_off", note = self.start_note + i, channel = self.channel )
                self.msg_queue.append(out_msg)
        self.n_match_old = n_match
    
    def toggle_device(self):
        print('switch active')
        self.device_active = not self.device_active

class state_switcher():
    ''' This class switches between states and does stuff on transitions

    '''
    def __init__(self, msg_queue, transition_fn = None, start_state = 0):
        self.state = start_state
        self.msg_queue = msg_queue
        if transition_fn is None:
            def transition_fn(queue, old_state, new_state):
                return
        self.transition_fn = transition_fn

    def set_state(self, state):
        self.transition(old_state = self.state, new_state = state)
        self.state = state

    def transition(self, old_state, new_state):
        self.transition_fn(self.msg_queue, old_state, new_state)