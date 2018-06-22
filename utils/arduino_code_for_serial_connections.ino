


int incomingByte = 0;   // for incoming serial data
int time_between = 100;

constexpr uint8_t n_lights = 10;
uint8_t buffer_array[n_lights];
static constexpr uint8_t startChar = 0; // or '!', or whatever your start character is

void setup() {
    Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
  
  // initialize digital pin 13 as an output.
  pinMode(13, OUTPUT);
   for (int i=0; i < 9; i++){
      buffer_array[i] = 100;
   }
}

void loop() {
        
    digitalWrite(13, HIGH);
    delay(time_between);
    digitalWrite(13, LOW);
    delay(time_between);
    
    // send data only when you receive data:
  
    //boolean storeString = false; //This will be our flag to put the data in our buffer
    //int index = 0;  //Initialize our index variable
    getLightLevels( buffer_array, sizeof( buffer_array));
    time_between = buffer_array[1];

}


void getLightLevels(uint8_t* buf, size_t buflen) {
      if (buf == nullptr) { return; }
      if (Serial.available() < (buflen + 1)) { return; }
      bool storeString = false;
      auto index = 0U;
      while(Serial.available() > 0){
        if (index == buflen) { break; }  // Reached the end of the array
        
        char incomingbyte = Serial.read();
        if(incomingbyte==startChar){
            storeString = true;
            continue;
            
        }
        if(storeString){
            buf[index++] = incomingbyte - 1;
       
        }        
    }
}


/*
 * 

# python code for sending serial

import serial
import time
import struct

ArduinoSerial = serial.Serial('COM14', 9600, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout=10)

# need to sleep so for serail to start
time.sleep(3)

#ArduinoSerial.write( b"$" )

in_array = [i*14 for i in range(8)]
in_array[1] = 200

def send_array(port, in_arr):
    if not len(in_arr) == 8:
        raise(ValueError("list has length "+ str(len(in_arr))+ "- it should be 8"))
    port.write(struct.pack('>B', 0))
    for i in range(len(in_arr)):
        if int(in_arr[i]) < 0 or int(in_arr[i]) > 255:
            raise(ValueError("invalid level at" + str(i) + " value " + str(int(in_arr[i])) ))
        send_value = int(in_arr[i])
        send_value = send_value + 1 # to avoid hitting 0 start bit
        send_value = min(send_value, 255) # to stop it sending 256 values once incremented
        port.write(struct.pack('>B', send_value))
    
send_array(ArduinoSerial, in_array)
# ArduinoSerial.write(struct.pack('>B', 0))s
# ArduinoSerial.write(struct.pack('>B', 0))
 
ArduinoSerial.close

*/
 