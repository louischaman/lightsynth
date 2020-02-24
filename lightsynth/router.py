from utils import maths
import functools
import numbers
import copy
import mido


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

def make_list_if_not(allowed):
    return [allowed] if not isinstance(allowed, list) else allowed

# eg cc mapping {'param':"attack" , 'scaling_fn': 'def_exp'}
def cc_action(control, param, scaling_fn=None, scaling_params=None, channel=None):
    if scaling_fn is None:
        scaling_fn = DEFAULT_LIN_SCALING_FN
    if scaling_params is None:
        scaling_params = {}
    if channel is None:
        channel = list(range(16))

    if isinstance(scaling_fn, str):
            # if the function parameter is a string then set fn from base_scaling_fns
        raw_func = base_scaling_fns[scaling_fn] 
        scaling_fn = functools.partial(raw_func, **scaling_params)
        assert isinstance(scaling_fn(100/127), numbers.Number),\
            'Scaling function should output a number'

    def cc_change(device, msg):
        device.set_param(param, scaling_fn(msg.value/127))

    filter_params = {
        'type':'control_change',
        'control': control,
        'channel': channel,
    }
    return action_mapping(filter_params = filter_params, action=cc_change, filter_type=mido.Message)

def pass_notes_action(filter_params = None):
    if filter_params is None:
        filter_params = {}
    filter_params.update({'type': ['note_on', 'note_off']})
    action = lambda device, msg: device.on_msg(msg)
    return action_mapping(filter_params = filter_params, action=action)

def pass_all_action(filter_params = None):
    action = lambda device, msg: device.on_msg(msg) 
    return action_mapping(action=action, filter_params=filter_params, filter_type=mido.Message)

def set_channel_action(channel):
    def switch_channel(device, msg):
        msg = copy.copy(msg)
        msg.channel = channel
        device.on_msg(msg) 
    return action_mapping(action=switch_channel,  filter_type=mido.Message)

def filter_msg(msg, filter_params):
    for param, allowed in filter_params.items():
        if not hasattr(msg, param):
                return True
        if getattr(msg, param) not in allowed:
            return True
    return False

def filter_type_check(msg, filter_types):
    if filter_types is ():
        return False
    if any([isinstance(msg, filter_type) for filter_type in filter_types]):
        return False
    return True

class action_mapping:
    def __init__(self, action, filter_params=None, filter_type=None):
        if filter_params is None:
            filter_params = {}

        if filter_type is None:
            filter_type = []

        self.filter_type = filter_type
        self.filter_params = filter_params
        self.action = action
        

        # change allowed values to a list if theyre not
        for param, allowed in self.filter_params.items():
            self.filter_params[param] = make_list_if_not(allowed)
        
        self.filter_type = tuple(make_list_if_not(self.filter_type))

    def do(self, device, msg):
        if filter_msg(msg, self.filter_params):
            return
            
        if filter_type_check(msg, self.filter_type):
            return
            
        self.action(device, msg)

# TODO make this simply add filters to other stuff
class deviceMap():
    ''' The mapping that tells the router which messages to send and what to do'''
    def __init__(self, device, filter_params=None, action_mappings=None, filter_type=None):
        if filter_params is None:
            filter_params = {}
        if filter_type is None:
            filter_type = []

        self.filter_params = copy.copy(filter_params)
        self.device = device
        self.action_mappings = action_mappings
        self.filter_type = filter_type
        self.filter_type = tuple(make_list_if_not(self.filter_type))
        
        # change allowed values to a list if theyre not
        for param, allowed in self.filter_params.items():
            self.filter_params[param] = make_list_if_not(allowed)

    
    def on_msg(self, msg):
        if filter_msg(msg, self.filter_params):
            return
        if filter_type_check(msg, self.filter_type):
            return

        for action_map in self.action_mappings:
            action_map.do(self.device, msg)
        

class midiRouterLI():
    ''' midiRouter takes midi messages and sends them to devices
    if a message is of type "note" it sends it straight to the device
    if a message is of type "cc" it maps it to parameters with scaling defined by 

    '''
    def __init__(self, device_mapping):
        self.device_mapping = device_mapping
        # add defaults

    def on_msg(self, msg):
        for mapping in self.device_mapping:
            mapping.on_msg(msg)

    def update_mapping(self, map_number, device_map):
        self.device_mapping[map_number] = device_map

