import lightsynth.router as rt
import lightsynth.light_instrument as li
from pprint import pprint
import mido
import time

light_inst = li.LightInstrumentGS(3)
cc_mapping = {
    1: "attack",
    2: "decay",
    4: "sustain",
    5: "release"
}

example_mapping = [
    {
        'device': light_inst,
        'note': {
            'channels': [0],
            'note_range': range(50,60)
        },
        'cc': {
            'channels': None,
            'cc_mapping': cc_mapping
        }
    }
]

mr = rt.midiRouterLI(mapping = example_mapping)

pprint(mr.mappings)

msg = mido.Message("note_on", note = 55 )
mr.on_msg(mido.Message("note_on", note = 55 ))
mr.on_msg(mido.Message("note_off", note = 55 ))

for i in range(10):
    print(light_inst.get_light_output())
    time.sleep(0.1)

mapping = mr.mappings[0]