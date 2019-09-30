import math


# Scaling functions
def float_to_int8_linear(value):
    """Scale a float in [0,1] linearly to an int in [0,255]."""
    ans = int(value * 255)
    ans = max(0, ans)
    ans = min(255, ans)
    return ans


def exp_scaling_fn(exp_rate, value_0_1):
    # scales from 0 to max_val exponentially so more control in low end
    return (math.pow(exp_rate, value_0_1) - 1) / (exp_rate - 1)


def float_to_int8_exp(value, exp_rate):
    """Scale a float in [0,1] exponentially to an int in [0,255]."""
    max_scaling = 0.4
    ans = exp_scaling_fn(exp_rate, value)
    ans = ans * 255
    ans = max(0, ans)
    ans = min(255, ans)
    ans = int(ans * max_scaling)
    return ans


class DMXDevice(object):
    """A base class for DMX devices.

    Subclasses must implement num_channels.
    """

    def __init__(self):
        self._dmx_port = None
        self._dmx_root = None
        self._values = None

    @property
    def dmx_port(self):
        return self._dmx_port

    @dmx_port.setter
    def dmx_port(self, value):
        self._dmx_port = value

    @property
    def dmx_root(self):
        return self._dmx_root

    @dmx_root.setter
    def dmx_root(self, value):
        self._dmx_root = value

    @property
    def num_channels(self):
        return None

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, new_values):
        if len(self.values) != self.num_channels:
            raise ValueError
        self._values = new_values

    def dmx_update(self):
        values_int8 = [self.scale_float_to_int8(x) for x in self.values]
        for offset, x in enumerate(values_int8):
            try:
                self.dmx_port.setChannel(self.dmx_root + offset, x)
            except Exception as error:
                print('Error setting dmx port {}, channel {} to {}'.format(
                    self.dmx_port, self.dmx_root + offset, x))
                raise(error)

    # default to exponential scaling with rate 1.7
    scaling_type = 'exponential'
    scaling_parameter = 1.7

    def scale_float_to_int8(self, value):
        if self.scaling_type == 'exponential':
            return float_to_int8_exp(value, self.scaling_parameter)
        elif self.scaling_type == 'linear':
            return float_to_int8_linear(value)
