import math
import yaml

from devices import Bulb, Par3RGB


# Helper function to generate lights in a grid
def gen_gs_grid(rows=4, cols=5, size=50,
                x_start=50, x_space=100,
                y_start=50, y_space=100,
                dmx_start=1, val=0.4):
    """
    Returns a list of gs lights with x and y positions as layed out in a grid
    with given number of rows and columns. The dmx roots are given in order
    starting from dmx_start, and the lights are initially assigned value val
    """
    gs_lights = [Bulb(None, 0, val, x, y, size)
                 for y in range(y_start, y_start + rows*y_space, y_space)
                 for x in range(x_start, x_start + cols*x_space, x_space)]
    for i, light in enumerate(gs_lights, dmx_start):
        light.dmx_root = i
        light.tag = str(i)

    return gs_lights

# Helper function to generate lights in a grid


def gen_rgb_grid(rows=1, cols=3, size=50,
                 x_start=50, x_space=100,
                 y_start=50, y_space=100,
                 dmx_start=1, r=0.4, g=0, b=0):
    """
    Returns a list of rgb lights with x and y positions as layed out in a grid
    with given number of rows and columns. The same dmx root is assigned to
    each light the lights are initially assigned given rgb values
    """
    tag = f'{dmx_start},{dmx_start+1},{dmx_start+2}'
    rgb_lights = [Par3RGB(None, dmx_start, [r, g, b], x, y, size, tag)
                  for y in range(y_start, y_start + rows*y_space, y_space)
                  for x in range(x_start, x_start + cols*x_space, x_space)]
    for i, light in enumerate(rgb_lights):
        dmx_root = i*3 + dmx_start
        light.dmx_root = dmx_root
        light.tag = f'{dmx_root},{dmx_root+1},{dmx_root+2}'
    return rgb_lights


# A grid layout of lights
def lights_grid():
    gs_lights = gen_gs_grid(rows=4, cols=5, size=50,
                            x_start=50, x_space=100,
                            y_start=50, y_space=100,
                            dmx_start=1, val=0.4)
    rgb_dmx_start = 1 + len(gs_lights)
    rgb_lights = gen_rgb_grid(rows=1, cols=5, size=50,
                              x_start=50, x_space=100,
                              y_start=450, y_space=100,
                              dmx_start=rgb_dmx_start, r=0.4, g=0, b=0)
    return gs_lights + rgb_lights


def lights_dome():
    val = 1
    size_s = 30
    size_m = 40
    size_l = 55
    alt_s_l = [size_s, size_l]

    centre_x = 250
    centre_y = 250
    inner_count = 5
    inner_radius = 100
    inner_start = 0
    outer_count = 10
    outer_radius = 200
    outer_start = 2*math.pi/20

    lights = []

    dmx_root = 1
    lights.append(Bulb(None, dmx_root, val, centre_x,
                       centre_y, size_m, str(dmx_root)))
    dmx_root += 1

    lights.extend(Bulb(None, d, val,
                       int(centre_x + inner_radius * math.cos(inner_start + 2*i*math.pi/inner_count)),
                       int(centre_y + inner_radius * math.sin(inner_start + 2*i*math.pi/inner_count)),
                       size_l, str(d))
                  for d, i in enumerate(range(inner_count), start=dmx_root))
    dmx_root += inner_count

    lights.extend(Bulb(None, d, val,
                       int(centre_x + outer_radius * math.cos(outer_start + 2*i*math.pi/outer_count)),
                       int(centre_y + outer_radius * math.sin(outer_start + 2*i*math.pi/outer_count)),
                       alt_s_l[i % 2], str(d))
                  for d, i in enumerate(range(outer_count), start=dmx_root))
    dmx_root += outer_count

    tag = f'{dmx_root},{dmx_root+1},{dmx_root+2}'
    lights.append(Par3RGB(None, dmx_root, [0.4, 0, 0],  50, 450, 50, tag))
    lights.append(Par3RGB(None, dmx_root, [0.4, 0, 0], 450, 450, 50, tag))

    return lights

def save_lights(lights, yaml_file):
    with open(yaml_file, 'w') as f:
        yaml.dump(lights, f)

if __name__ == '__main__':
    lights = lights_grid()
    save_lights(lights, 'lights_grid.yaml')

    lights = lights_dome()
    save_lights(lights, 'lights_dome.yaml')
