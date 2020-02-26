import serial
import time
import struct

ArduinoSerial = serial.Serial('COM14', 9600, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout=0.1)
time.sleep(3)

#ArduinoSerial.write( b"$" )

in_array = [200 for i in range(10)]
#in_array[1] = 200

for i in range(5):
    print(ArduinoSerial.readline())

time.sleep(1)

def send_array(port, in_arr):
    if not len(in_arr) == 10:
        raise(ValueError("list has length "+ str(len(in_arr))+ "- it should be 10x"))
    port.write(struct.pack('>B', 0))
    for i in range(len(in_arr)):
        if int(in_arr[i]) < 0 or int(in_arr[i]) > 255:
            raise(ValueError("invalid level at" + str(i) + " value " + str(int(in_arr[i])) ))
        send_value = int(in_arr[i])
        send_value = send_value + 1 # to avoid hitting 0 start bit
        send_value = min(send_value, 255) # to stop it sending 256 values once incremented
        port.write(struct.pack('>B', send_value))
    
send_array(ArduinoSerial, in_array)
ArduinoSerial.flushOutput()
ArduinoSerial.flushInput()

print("after sent")
for i in range(5):
    print(ArduinoSerial.readline())
# ArduinoSerial.write(struct.pack('>B', 0))s
# ArduinoSerial.write(struct.pack('>B', 0))
 
ArduinoSerial.close()