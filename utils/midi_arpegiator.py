import mido
import time
import random

'''
goes through the notes pressed down and plays them in sequence

'''

class arpeggiator():
    def __init__(self, rate = 240, order = range(25), randomise = True):
        '''
        set up 
            whether up or down 
            rate
            notes_list
        '''
        self.notes_on = [False] * 128
        self.next_note_time = 0
        self.rate = rate# in bpm
        self.note_i = 0
        self.order = order
        self.note_playing = False
        self.randomise = randomise
        self.next_note_play = 0

    def randomise_order(self):
        random.shuffle(self.order)

    def notes_on_list(self):
        # returns list of notes that are pressed
        return [i for i, note_on in enumerate(self.notes_on) if note_on]
    
    def notes_on_list_order(self):
        # returns list of notes that are pressed
        nt_on = self.notes_on_list()

        if len(self.order) < len(nt_on):
            raise(ValueError("not enough notes in order"))

        ord_cuttoff = self.order[:len(nt_on)]
        ord_less = sorted(range(len(ord_cuttoff)),key=ord_cuttoff.__getitem__)
        for ind, pos in enumerate(ord_less):
            ord_cuttoff[pos] = ind
        return [ nt_on[i] for i in ord_cuttoff  ]

    def note_msg(self, msg):
        # change notes_on either note on or off
        if msg.type == "note_on":
            # if first note to be pressed start arpegiator
            if not self.notes_on_list():
                self.next_note_time = time.time()
                self.next_note_play = msg.note
                
            self.notes_on[msg.note] = True

        if msg.type == "note_off":
            
            # if removing next note to play make it the next one
            if self.next_note_play == msg.note and self.notes_on_list():
                self.shift_next_note()
            
            self.notes_on[msg.note] = False

    def shift_next_note(self):
            nt_list = self.notes_on_list_order()
            note_i = (nt_list.index(self.next_note_play) + 1) % len(nt_list)
            self.next_note_play = nt_list[note_i]


    def get_notes(self):
        # either returns a note or returns nothing
        notes_out = []
        if time.time() > self.next_note_time:
            if self.notes_on_list():
                # if there are some notes down
                notes_out.append(self.next_note_play)
                self.next_note_time = time.time() + float(60) / self.rate 
                self.shift_next_note()

            
                if  not self.note_playing:
                    if self.randomise:
                        self.randomise_order()
                    # if its first note then not note playing
                    self.note_playing = notes_out[0]
                    return [mido.Message('note_on', note = notes_out[0], velocity = 127)]


                elif self.note_playing:
                    # if middle note then off last
                    output_list = [mido.Message('note_off', note = self.note_playing), mido.Message('note_on', note = notes_out[0]) ]
                    self.note_playing = notes_out[0]
                    return output_list

            elif self.note_playing:
                output_list = [mido.Message('note_off', note = self.note_playing) ]
                self.note_playing = False
                return output_list
        
        return []


if __name__=="__main__":
    arp = arpeggiator(rate = 60*3)
    notes_chord =[mido.Message('note_on', note=note + 50) for note in [0,5,12]]
    notes_chord_off =[mido.Message('note_off', note=note + 50) for note in [0,5,12]]
    start_time = time.time()
    for note in notes_chord:
        arp.note_msg(note)

    while notes_chord_off:
        for note in arp.get_notes():
            print note
        
        if time.time()>start_time + 1 :
            arp.note_msg(notes_chord_off.pop())
            start_time = time.time()

