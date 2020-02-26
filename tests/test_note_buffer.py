from utils.miditools import noteBuffer
import mido
note_buff = noteBuffer(10)
seq = [41,42,43]
# note_buff.count_notes_match([41,42,43])

note_buff.on_msg(mido.Message("note_on", note = 55 ))
note_buff.on_msg(mido.Message("note_off", note = 55 ))

print(note_buff.count_notes_match(seq))

for i in seq:
    note_buff.on_msg(mido.Message("note_on", note = i ))
    note_buff.on_msg(mido.Message("note_off", note = i ))
    print(note_buff.count_notes_match(seq))

note_buff.get_last(3)
note_buff.note_buffer

self = note_buff
