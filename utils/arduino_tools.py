
import serial
from list_ports import serial_ports
from pprint import pprint
import struct

def send_array(port, in_arr):
    if not len(in_arr) == 10:
        raise(ValueError("list has length "+ str(len(in_arr))+ "- it should be 10x"))
        
    port.flushOutput()
    port.write(struct.pack('>B', 0))
    for i in range(len(in_arr)):
        if int(in_arr[i]) < 0 or int(in_arr[i]) > 255:
            raise(ValueError("invalid level at" + str(i) + " value " + str(int(in_arr[i])) ))
        send_value = int(in_arr[i])
        send_value = send_value + 1 # to avoid hitting 0 start bit
        send_value = min(send_value, 255) # to stop it sending 256 values once incremented
        port.write(struct.pack('>B', send_value))
    

def user_serial():
    #get dmx devices from user input
    available_ports = serial_ports()
    if len(available_ports ) > 0:
        pprint([ (i, available_ports[i]) for i in range(len(available_ports))] )
        which_port = int(raw_input('select serial port number: '))
        
        dmx_port = serial.Serial(available_ports[which_port], 115200, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout=0.1)
    else:
        print("no_dmx")
        dmx_port = {}
    return(dmx_port)
