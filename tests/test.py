import utils.miditools as mt
import mido 

# note store test
msg = mido.Message("note_on", note = 1 )
msg = mido.Message("note_off", note = 1 )

note_store = mt.noteStore()
note_store.on_msg(mido.Message("note_on", note = 1 ))
assert (note_store.which_notes_on() == [1])
note_store.on_msg(mido.Message("note_off", note = 1 ))
assert (note_store.which_notes_on() == [])


# note buffer test
note_buffer = mt.noteBuffer(3)
note_buffer.on_msg(mido.Message("note_on", note = 1 ))
assert(note_buffer.get_last(1) == [1])
note_buffer.on_msg(mido.Message("note_on", note = 2 ))
assert(list(note_buffer.note_buffer) == [1,2])

for i in range(3):
    note_buffer.on_msg(mido.Message("note_on", note = 2 ))
assert(list(note_buffer.note_buffer) == [2,2,2])

# insttest
from lightsynth import light_instrument as li
import time
light_inst = li.LightInstrumentGS(10)



light_inst.on_msg(mido.Message("note_on", note = 2 ))
light_inst.note_light
light_inst.on_msg(mido.Message("note_off", note = 2 ))
for i in range(4):
    light_inst.on_msg(mido.Message("note_on", note = 2 ))
    light_inst.on_msg(mido.Message("note_off", note = 2 ))
    time.sleep(0.1)
    print(light_inst.get_light_output())

light_inst.note_light