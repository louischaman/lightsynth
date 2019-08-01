from .dmx_device import DMXDevice


class Par3RGB(DMXDevice):
    """A 3-channel RGB parcan.

    A Par3RGB has a `value` representing RGB brightness levels which is list 
    of three floats in [0,1], attributes `x` and `y` representing location, 
    and an attribute for `size`. The attribute `tag` is an arbitrary string 
    for the demo to display. The method `dmx_update` sends brighness messages
    for R, G, and B to channels `dmx_root`,  `dmx_root+1`, `dmx_root+2` on the
    port `dmx_port`. The values sent are appropraitely scaled to ints in 
    [0,255].
    """

    def __init__(self, dmx_port=None, dmx_root=0, values=[0.4, 0, 0], x=0, y=0, size=50, tag=''):
        self._dmx_port = dmx_port
        self._dmx_root = dmx_root
        self._values = values

        self.x = x
        self.y = y
        self.size = size
        self.tag = tag

    @property
    def num_channels(self):
        return 3
