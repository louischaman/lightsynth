import bisect
import copy
import yaml
import miditools as mt

def get_nearest_note(note, scale):
    scale = copy.copy(scale) + [12]
    i = bisect.bisect_left(scale,note)
    return (scale[i])

def generate_scale_mapping(scale):
    in_notes = range(150)
    note_letter = [(note-21) % 12 for note in in_notes]
    octave = [(in_notes[i] - note_letter[i] + 3)/12 - 2   for i in in_notes]
    scale_letter = [ get_nearest_note(note, scale) for note in note_letter ]
    mapping = [scale_letter[i] + octave[i] * 12  for i in in_notes]
    return(mapping[21:150])

# scale = [0,2,3,5,7,8,10]
# print( generate_scale_mapping(scale))

stream = open("utils/scales.yaml", "r")
scales = dict(yaml.load(stream))
print(scales)

# mapping = generate_scale_mapping( scales['flamenco'] )
# print(mapping)


if __name__=="__main__":
    port_dict = mt.user_midi()
    out_dict = mt.user_midi_output()

    while 1:
        for device, midi_port_in in port_dict.iteritems():
            for device, midi_out_port in out_dict.iteritems():

                # if two cc messages with the same control and channel have come then only append most recent
                for msg in midi_port_in.iter_pending():
                    msg = mt.map_note(mapping, msg)
                    print(msg)
                    
                    midi_out_port.send(msg)