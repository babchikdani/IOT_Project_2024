#include <HardwareSerial.h> // Reference the ESP32 built-in serial port library
#include <ESP32Servo.h>
#include <string>

using std::string;


Servo myservo;
int servoPin = 15;

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

HardwareSerial lidarSerial(2); // Using serial port 2

uint8_t sys_speed=1;     // metrics[0]
uint8_t sys_max_angle=180; // metrics[1], in degrees.
uint8_t sys_min_angle=0; // metrics[2], in degrees.
uint8_t sys_max_dist=700;  // metrics[3], in centimeters.
uint8_t sys_min_dist=50;  // metrics[4], in centimeters.
uint8_t sys_start_cmd=1; // metrics[5], 1 to start. 0 to stop.
uint8_t metrics[NUM_OF_PC_INPUTS];


inline void send_to_pc(string str){
  for(int k=0; k<str.size(); k++){
    Serial.write(str[k]);
  }
  // delay(100);
}

inline int read_distance(){
  uint8_t buf[9] = {0}; // An array that holds data
  uint16_t distance;
  if (lidarSerial.available() > 0) {
    lidarSerial.readBytes(buf, 9); // Read 9 bytes of data
    if( buf[0] == 0x59 && buf[1] == 0x59)
    {
      distance = buf[2] + buf[3] * 256;
      // uint16_t strength = buf[4] + buf[5] * 256;
      // int16_t temperature = buf[6] + buf[7] * 256;
    }
  }
  delay(10);
  return int(distance);
}

inline void print_sys_metrics(){
  Serial.print("sys_speed = ");
  Serial.println(sys_speed);
  Serial.print("sys_max_angle = ");
  Serial.println(sys_max_angle);
  Serial.print("sys_min_angle = ");
  Serial.println(sys_min_angle);
  Serial.print("sys_max_dist = ");
  Serial.println(sys_max_dist);
  Serial.print("sys_min_dist = ");
  Serial.println(sys_min_dist);
  Serial.print("sys_start_cmd = ");
  Serial.println(sys_start_cmd);
}

inline void servo_init(){
  ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	myservo.setPeriodHertz(50);    // standard 50 hz servo
	myservo.attach(servoPin, SERVO_MIN_PWM, SERVO_MAX_PWM); // attaches the servo on pin 15 to the servo object
}

inline void update_sys_metrics(){
  sys_speed = metrics[0];
  sys_max_angle = metrics[1];
  sys_min_angle = metrics[2];
  sys_max_dist = metrics[3];
  sys_min_dist = metrics[4];
  sys_start_cmd = metrics[5];
}

inline void blink_times(int n){
  for(int ii=0; ii<n; ii++){
    digitalWrite(LED_BUILTIN, HIGH);
    delay(100);
    digitalWrite(LED_BUILTIN, LOW);
    delay(100);
  }
}

inline string build_string(int dist, int angle){
  string tmp_dist = std::to_string(dist);
  while(tmp_dist.size() < 3){
    tmp_dist = "0"+tmp_dist;
  }
  string tmp_angle = std::to_string(angle);
    while(tmp_angle.size() < 3){
    tmp_angle = "0"+tmp_angle;
  }
  return tmp_dist+"_"+tmp_angle;
}

inline void move_servo_to(int pos){
  myservo.write(pos);
  delay(15);
}

void setup() {
  Serial.begin(115200); // Initializing serial port
  lidarSerial.begin(115200, SERIAL_8N1, RXD2, TXD2); // Initializing serial port
  servo_init();
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // if(sys_start_cmd == 0){
  //   digitalWrite(LED_BUILTIN, HIGH);
  //   delay(500);
  // } else { // we're on.
    blink_times(10);
    // sweep left
    int cur_dist;
    for(int pos=0; pos<=180; pos++){
      move_servo_to(pos);
      cur_dist = read_distance();   // in cm
      if(cur_dist > sys_min_dist && cur_dist < sys_max_dist){
        string tmp_str = build_string(cur_dist, pos);
        send_to_pc(tmp_str);
      }
    }
    // sweep right.
    for(int pos=180; pos>=0; pos--){
      move_servo_to(pos);
      cur_dist = read_distance();   // in cm
      if(cur_dist > sys_min_dist && cur_dist < sys_max_dist){
        string tmp_str = build_string(cur_dist, pos);
        send_to_pc(tmp_str);
      }
    }
  // }
  //   if(Serial.available() > 0) { // Check if new data is available to read
  //     delay(300); // for all of the information to arrive by serial communication.
  //     Serial.readBytes(metrics, NUM_OF_PC_INPUTS);
  //     update_sys_metrics();
  //     string str = "recieved new metrics!";
  //     // send_to_pc(str);
  //     // print_sys_metrics();
  //     delay(300);
  // } else {
  //   string str = "current sys metrics!";
  //   // send_to_pc(str);
  //   // print_sys_metrics();
  //   delay(300);
  // }

}
