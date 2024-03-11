#include <HardwareSerial.h> // Reference the ESP32 built-in serial port library
#include <ESP32Servo.h>
#include <string>

using std::string;


Servo myservo;
int servoPin = 15;

HardwareSerial lidarSerial(2); // Using serial port 2
// HardwareSerial guiSerial(5);    // command serial port

#define RXD2 13
#define TXD2 12
#define SERVO_MIN_PWM 544
#define SERVO_MAX_PWM 2400
#define STOP 0
#define START 1
#define BAD_READ (-1)
#define LiDAR_MIN_SIGNAL_STRENGTH 100 
#define LiDAR_MIN_DISTANCE 30 // in cm
#define INT_MAX 2147483647
#define UINT16_T_MAX 65535
#define NUM_OF_PC_INPUTS 6 

uint8_t sys_speed=0;     // metrics[0]
uint8_t sys_max_angle=0; // metrics[1], in degrees.
uint8_t sys_min_angle=0; // metrics[2], in degrees.
uint8_t sys_max_dist=0;  // metrics[3], in meters.
uint8_t sys_min_dist=0;  // metrics[4], in meters.
uint8_t sys_start_cmd=0; // metrics[5], 1 to start. 0 to stop.
uint8_t metrics[NUM_OF_PC_INPUTS];

inline void send_ack(string str){
  while(!Serial.availableForWrite()) {}
  for(int k=0; k<str.size(); k++){
    Serial.write(str[k]);
  }
}

inline void servo_init(){
  ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	myservo.setPeriodHertz(50);    // standard 50 hz servo
	myservo.attach(servoPin, SERVO_MIN_PWM, SERVO_MAX_PWM); // attaches the servo on pin 18 to the servo object
}

inline uint16_t read_distance(){
  uint8_t buf[9] = {0}; // An array that holds data
  uint16_t distance;
  if (lidarSerial.available() > 0) {
    lidarSerial.readBytes(buf, 9); // Read 9 bytes of data
    if( buf[0] == 0x59 && buf[1] == 0x59)
    {
      distance = buf[2] + buf[3] * 256;
      uint16_t strength = buf[4] + buf[5] * 256;
      // int16_t temperature = buf[6] + buf[7] * 256;
    }
  }
  delay(10);
  return distance;
}

inline void update_sys_metrics(uint8_t* new_metrics){
  sys_speed = new_metrics[0];
  sys_max_angle = new_metrics[1];
  sys_min_angle = new_metrics[2];
  sys_max_dist = new_metrics[3];
  sys_min_dist = new_metrics[4];
  sys_start_cmd = new_metrics[5];
}

inline void move_servo_to(int pos){
  myservo.write(pos);
  delay(15);
}

inline void send_target_data(uint16_t range, uint16_t angle){
  while(!Serial.availableForWrite()) {}
  Serial.write(range);
  while(!Serial.availableForWrite()) {}
  Serial.write(angle);
}


void setup() {
  Serial.begin(115200); // Initializing serial port
  lidarSerial.begin(115200, SERIAL_8N1, RXD2, TXD2); // Initializing serial port
  servo_init();
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.flush();
}

inline void blink_times(int n){
  for(int ii=0; ii<n; ii++){
    digitalWrite(LED_BUILTIN, HIGH);
    delay(100);
    digitalWrite(LED_BUILTIN, LOW);
    delay(100);
  }
}

void loop() {
  if(sys_start_cmd == 0){
    digitalWrite(LED_BUILTIN, HIGH);
  } else { // we're on.
    blink_times(10);
    // sweep left
    uint16_t cur_dist;
    for(int pos=sys_min_angle; pos<=sys_max_angle; pos++){
      move_servo_to(pos);
      cur_dist = read_distance();
      if(cur_dist > sys_min_dist && cur_dist < sys_max_dist){
        send_target_data(cur_dist, (uint16_t)pos);
      }
    }

    // sweep right
    for(int pos=sys_max_angle; pos>=sys_min_angle; pos--){
      move_servo_to(pos);
      cur_dist = read_distance();
      if(cur_dist > sys_min_dist && cur_dist < sys_max_dist){
        send_target_data(cur_dist, (uint16_t)pos);
      }
    }
  }
  if(Serial.available()) { // Check if new data is available to read
      Serial.readBytes(metrics, NUM_OF_PC_INPUTS);
      update_sys_metrics(metrics);
      string str = "recieved new metrics!\n";
      send_ack(str);
  }
}
