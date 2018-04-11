import pysimpledmx
mydmx = pysimpledmx.DMXConnection("COM11")

#mydmx.setChannel(0, 255)
mydmx.setChannel(1, 255) # set DMX channel 1 to full
#mydmx.setChannel(2, 100) 
mydmx.render()
# set DMX channel 1 to full
mydmx.setChannel(3, 100) 
mydmx.render()