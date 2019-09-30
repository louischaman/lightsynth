from .dmx_device import DMXDevice


class Bulb(DMXDevice):
    """A 1-channel dimmable bulb.

    For a bule Bulb `values` has a single entry representing brightness which 
    is a float in [0,1]. 

    The attributes `x`, `y`, and `size` control display in the demo, and `tag`
    is an arbitrary string for the demo to display.

    The method `dmx_update` from DMXDevice sends a brighness message to channel
    `dmx_root` on the port `dmx_port`. The values are scaled to an int in 
    [0,255] before sending.
    """

    def __init__(self, dmx_port=None, dmx_root=1, value=0.4, x=0, y=0, size=50, tag=''):
        self._dmx_port = dmx_port
        self._dmx_root = dmx_root
        self._values = [value]
        self.x = x
        self.y = y
        self.size = size
        self.tag = tag

    @property
    def num_channels(self):
        return 1
