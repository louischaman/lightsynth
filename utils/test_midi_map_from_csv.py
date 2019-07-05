import csv
import miditools as mt

port_dict = mt.user_midi()

reader = csv.reader(open('utils/scale.csv', 'r'))
next(reader)
mapping = {}
for row in reader:
   note_name, in_note, out_note = row
   mapping[int(in_note)] = int(out_note)

while 1:
    for device, midi_port in port_dict.items():
        for msg in midi_port.iter_pending():
            msg = mt.map_note(mapping, msg)
            print(msg)
            