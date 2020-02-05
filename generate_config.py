import utils.configuration as conf
from devices import Bulb, Par3RGB

lights_file = 'vlight/demo/lights_grid.yaml'
lights = conf.load_lights(lights_file)
envelope_params = {
    'attack': 0.1,
    'decay': 2,
    'sustain': 1,
    'release': 2,
}

lights_bulbs = [light for light in lights if isinstance(light, Bulb)]
lights_rgbs = [light for light in lights if isinstance(light, Par3RGB)]

print(f'Found {len(lights_bulbs)} Bulbs and {len(lights_rgbs)} Par3RGBs')

gs_instrument_input = dict(
    n_lights=len(lights_bulbs),
    envelope_params=envelope_params,
    mode="follow"
)
rgb_intrument_input = dict(
        n_lights=len(lights_rgbs),
        envelope_params=envelope_params,
        mode="follow")
