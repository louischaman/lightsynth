# imports needed for loading light setup
import _yaml as yaml
from devices import Bulb, Par3RGB

add_library('oscP5')

lights_file_full_path = '/Users/ewan/git/lightsynth/vlight/demo/lights_grid.yaml'

def load_lights():
    if lights_file_full_path is None:
        print('Error: you must specify a lights file by setting `lights_file_full_path` in code')
    with open(lights_file_full_path) as f:
        lights = yaml.load(f, Loader=yaml.FullLoader)
    return lights

# load the light config from a file
lights = load_lights()
cur_channel = 1
num_channels = max([light.dmx_root + light.num_channels - 1 for light in lights])

# setup some global variables
osc = None
loc = None

padding = 0
min_x = min([light.x + light.size for light in lights])
min_y = min([light.y + light.size for light in lights])
max_x = max([light.x + light.size for light in lights])
max_y = max([light.y + light.size for light in lights])

win_width = max_x + padding
win_height = max_y + padding

if min_x < 0 or min_y < 0:
    print('Error: lights must lie fully in the non-negative orthand')

print('Setting width = {} and height = {} to fit all the lights in the window'.format(win_width, win_height))

framerate = 25
osc_port = 12000
font = None
font_height = 12
text_color = 255

def setup():
    global osc, loc, oscEvent, font
                    
    size(win_width, win_height)
    frameRate(framerate)
    font = createFont("Arial", 16, True)
    textFont(font, font_height)
 
    # start oscP5 by default listening on port 12000
    osc = OscP5(this, osc_port)
    loc = NetAddress('127.0.0.1', osc_port)
    
def draw_light(light):
    fill(*light.values)
    ellipse(light.x, light.y, light.size, light.size)  
    fill(text_color)
    textAlign(CENTER)
    text(light.tag, light.x, light.y+font_height/2)
    
def draw():
    background(0)
    
    for light in lights:
         draw_light(light)
         
def mousePressed():
    global cur_channel
    print('### mouse pressed')
    print('### messaging channel %d' % cur_channel)
    
    msg = OscMessage("/dmx") 
    msg.add(cur_channel) 
    msg.add(200)
    
    print('sending message: %s' % msg)
    osc.send(msg, loc) 
    cur_channel = 1 + (cur_channel % num_channels)
    
# declare oscEvent first so it's caught in the setup phase
def oscEvent(msg):
    if msg.checkAddrPattern('/dmx') and msg.checkTypetag('ii'):
        channel = msg.get(0).intValue()
        value = msg.get(1).intValue()

        print('### received osc message: set channel %3d to %3d' % (channel, value))
        
        for light in lights:          
            if light.dmx_root <= channel and channel < light.dmx_root + light.num_channels:
                offset = channel - light.dmx_root
                light.values[offset] = value
           
# This function is important else the OSC listening server doesn't shut down
# and blocks any new instance from listening on the same port
def stop():
    print('### quitting...')
    osc.stop()
    print('### done.')
    
def keyPressed():
    global lights, cur_channel
    if key == 'r':
        print('### resetting')
        lights = load_lights()
        cur_channel = 1