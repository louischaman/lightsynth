from utils import maths
import functools
import numbers


def linear_scaling_fn(x, out_range):
    return maths.linear_scaling_in_01(x, out_range[0], out_range[1])

def exponential_scaling_fn(x, out_range, exp_rate):
    return maths.exp_scaling_min_max(x, min_val = out_range[0], max_val = out_range[1], exp_rate =exp_rate)

DEFAULT_CHANNEL_RANGE = list(range(12))
DEFAULT_NOTE_RANGE = list(range(127))
DEFAULT_CC_MAPPING = {}
DEFAULT_CC_EXP_SCALING = 3

DEFAULT_NOTE = {
    'channels': DEFAULT_CHANNEL_RANGE,
    'note_range': DEFAULT_NOTE_RANGE
}

DEFAULT_CC = {
    'channels': DEFAULT_CHANNEL_RANGE,
    'cc_mapping': DEFAULT_CC_MAPPING
}

DEFAULT_LIN_SCALING_FN = lambda x:x
DEFAULT_EXP_SCALING_FN = functools.partial(exponential_scaling_fn, out_range = (0,5), exp_rate =5)

base_scaling_fns = {
    'def_lin': DEFAULT_LIN_SCALING_FN,
    'def_exp': DEFAULT_EXP_SCALING_FN,
    'lin': linear_scaling_fn,
    'exp': exponential_scaling_fn,
}


def update_dict(dict_here, key, default):
    dict_here[key] = dict_here.get(key, default)
    if dict_here[key] is None: 
        dict_here[key] = default


class midiRouterLI():
    ''' midiRouter takes midi messages and sends them to devices
    if a message is of type "note" it sends it straight to the device
    if a message is of type "cc" it maps it to parameters with scaling defined by 

    '''
    def __init__(self, mapping, midi_default_pass = True):
        self.mappings = mapping
        self.midi_default_pass = midi_default_pass
        # add defaults
        for device_map in self.mappings:
            # this can probably be done better with classes for each mapping type
            update_dict(device_map, 'channels', DEFAULT_CHANNEL_RANGE)
            update_dict(device_map, 'note', DEFAULT_NOTE)
            update_dict(device_map, 'cc', DEFAULT_CC)

            note_mapping = device_map['note']
            update_dict(note_mapping, 'channels', DEFAULT_CHANNEL_RANGE)
            update_dict(note_mapping, 'note_range', DEFAULT_NOTE_RANGE)

            cc = device_map['cc']
            update_dict(cc, 'channels', DEFAULT_CHANNEL_RANGE)
            update_dict(cc, 'cc_mapping', DEFAULT_CC_MAPPING)

            cc_mapping = cc['cc_mapping']
            for key, cc_map in cc_mapping.items():
                if isinstance(cc_map, str):
                    cc_mapping[key] = {'param': cc_map}
                # scaling_fn can be a custom function that takes one input in range (0,1) 
                # or it can be a string which maps to one of the functions specified in the 
                # base_scaling_fns with the params as whatever parameters it needs
                update_dict(cc_mapping[key], 'scaling_fn', DEFAULT_LIN_SCALING_FN)
                if isinstance(cc_mapping[key]['scaling_fn'], str):
                    # if the function parameter is a string then set fn from base_scaling_fns
                    raw_func = base_scaling_fns[cc_mapping[key]['scaling_fn']] 
                    # default params is an empty dict
                    params = cc_mapping[key].get('params',{})
                    cc_mapping[key]['scaling_fn'] = functools.partial(raw_func, **params)
                    assert isinstance(cc_mapping[key]['scaling_fn'](100/127), numbers.Number),\
                        'Scaling function should output a number'
                
    def on_msg(self, msg):
        for mapping in self.mappings:
            if not msg.channel in mapping['channels']:
                continue

            if msg.type in ['note_on','note_off']:
                if not mapping['type'] == 'midi':
                    continue
                if not msg.channel in mapping['note']['channels']:
                    continue
                if not msg.note in mapping['note']['note_range']:
                    continue
                mapping['device'].on_msg(msg)

            elif msg.type == 'control_change':
                if not msg.channel in mapping['cc']['channels']:
                    continue
                if not msg.control in mapping['cc']['cc_mapping']:
                    continue
                cc_mapping = mapping['cc']['cc_mapping'][msg.control]
                value = cc_mapping['scaling_fn'](msg.value/127)
                mapping['device'].set_param(cc_mapping['param'], value)
            
            elif self.midi_default_pass:
                mapping['device'].on_msg(msg)
