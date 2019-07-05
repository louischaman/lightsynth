/**
 * oscP5sendreceive by andreas schlegel
 * example shows how to send and receive osc messages.
 * oscP5 website at http://www.sojamo.de/oscP5
 */
 
import oscP5.*;
import netP5.*;
  
OscP5 oscP5;
NetAddress myRemoteLocation;

int n_gs_lights = 20;

int n_rgb_lights = 3;

int sep = 250;
int sep2 = 100;

int[] x_coords = new int[n_gs_lights + n_rgb_lights];
int[] y_coords = new int[n_gs_lights + n_rgb_lights];
int[] light_vals = new int[n_gs_lights];
int[] light_vals_rgb = new int[n_rgb_lights * 3];

void setup() {
  size(1500,1000);
  frameRate(25);
  /* start oscP5, listening for incoming messages at port 12000 */
  oscP5 = new OscP5(this,12000);

    
  
  
  for(int i = 0; i< (n_gs_lights ); i = i+1){
    x_coords[i] = (sep * i ) % width + sep/2;
    y_coords[i] = sep *( (sep * i )/width )+ sep/2;
    light_vals[i] = 100;
    fill(light_vals[i]);
      ellipse(x_coords[i], y_coords[i], sep2, sep2);
  }

    for(int i = 0; i< (n_rgb_lights ); i = i+1){
    x_coords[i + n_gs_lights] = (sep * (i+ n_gs_lights) ) % width + sep/2;
    y_coords[i + n_gs_lights] = sep *( (sep * (i+ n_gs_lights) )/width )+ sep/2;
    light_vals_rgb[i*3] = 100;
    light_vals_rgb[i*3+1] = 0;
    light_vals_rgb[i*3+2] = 0;
    fill(light_vals_rgb[i],light_vals_rgb[i+1],light_vals_rgb[i+2]);
      ellipse(x_coords[i + n_gs_lights], y_coords[i+ n_gs_lights], sep2, sep2);
  }
  /* myRemoteLocation is a NetAddress. a NetAddress takes 2 parameters,
   * an ip address and a port number. myRemoteLocation is used as parameter in
   * oscP5.send() when sending osc packets to another computer, device, 
   * application. usage see below. for testing purposes the listening port
   * and the port of the remote location address are the same, hence you will
   * send messages back to this sketch.
   */
  myRemoteLocation = new NetAddress("127.0.0.1",12000);
}


void draw() {
  background(0); 
    for(int i = 0; i< n_gs_lights; i = i+1){
    fill(light_vals[i]);
      ellipse(x_coords[i], y_coords[i], sep2, sep2);
  }
      for(int i = 0; i< (n_rgb_lights ); i = i+1){
    fill(light_vals_rgb[i*3],light_vals_rgb[i*3+1],light_vals_rgb[i*3+2]);
      ellipse(x_coords[i + n_gs_lights], y_coords[i+ n_gs_lights], sep2, sep2);
  }
  
  
}

void mousePressed() {
  /* in the following different ways of creating osc messages are shown by example */
  OscMessage myMessage = new OscMessage("/dmx");
  
  myMessage.add(0); /* add an int to the osc message */
  myMessage.add(200); /* add an int to the osc message */

  /* send the message */
  oscP5.send(myMessage, myRemoteLocation); 
}


/* incoming osc message are forwarded to the oscEvent method. */
void oscEvent(OscMessage theOscMessage) {
  
  if(theOscMessage.checkAddrPattern("/dmx")==true) {
    /* check if the typetag is the right one. */
    if(theOscMessage.checkTypetag("ii")) {
      /* parse theOscMessage and extract the values from the osc message arguments. */
      int position = theOscMessage.get(0).intValue();  
      int value = theOscMessage.get(1).intValue();
      if(position < n_gs_lights){
        light_vals[position] = value;
      }
      else{
        println(position, value);
        light_vals_rgb[position -  n_gs_lights] = value;
      }
      
      return;
    }  
  } 
  
}