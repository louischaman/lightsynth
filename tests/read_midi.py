import mido
import utils.miditools as mt
import time
import lightsynth.generator as gn
import collections
out_port = list(mt.user_midi_output().values())[0]

filename =  r"C:\Users\louisdell\Downloads\twinkle_twinkle.mid"



midi_file = mido.MidiFile(filename)
time_through = 0
msg_sequence = []
for msg in list(midi_file):
    print(msg)
    if not msg.is_meta:
        msg_time = msg.time
        msg.time = 0
        # if msg.type in ['note_on']:
        #     msg.velocity = 64
        time_through = time_through + msg_time
        if msg.type in ['note_on', 'note_off']:
            msg_sequence.append((round(time_through,5), msg))


time_through

queue = collections.deque()
ms = gn.appendMsgSequence(queue, msg_sequence, auto_sort=False, repeat= time_through +0.001 )

try:
    # pprint(ms.msg_sequence[::-1])
    ms.start()
    # pprint(ms.msg_sequence[::-1])
    while 1:
        if len(queue)>0:
            # pprint(ms.msg_sequence[::-1])
            msg = queue.popleft()
            print(msg)
            out_port.send(msg)
except KeyboardInterrupt:
    # quit
    ms.stop()


from pprint import pprint 
pprint(ms.msg_sequence[:-15:-1])
pprint(msg_sequence[:5])
