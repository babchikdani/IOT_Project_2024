#include <HardwareSerial.h> // Reference the ESP32 built-in serial port library
#include <ESP32Servo.h>
#include <string>

using std::string;


Servo myservo;
int servoPin = 15;

#define ROOM_SCAN_DONE_SIGNAL "Room Scan Done!\n"
#define BAUD_RATE 115200
#define FLASHLIGHT_PIN 23
#define RX_PIN 16
#define TX_PIN 17
#define SERVO_MIN_PWM 544
#define SERVO_MAX_PWM 2400
#define STOP 0
#define START 1
#define BAD_READ (-1)
#define LiDAR_MIN_SIGNAL_STRENGTH 100 
#define LiDAR_MIN_DISTANCE 30 // in cm
#define INT_MAX 2147483647
#define UINT16_T_MAX 65535
#define NUM_OF_PC_INPUTS 8
#define BUFFER_SIZE 1024
#define FULL_SCAN 181
HardwareSerial lidarSerial(2); // Using serial port 2

int sys_speed=1;     // 1, 2, or 3.
int sys_max_angle=180; // in degrees.
int sys_min_angle=0; // in degrees.
int sys_max_dist=700;  // in centimeters.
int sys_min_dist=50;  // in centimeters.
int sys_start_cmd=0; // 1 to start. 0 to stop. 2 for room scan.
uint8_t metrics[NUM_OF_PC_INPUTS];
int room_distances[FULL_SCAN];
int last_scan[FULL_SCAN];


inline void send_to_pc(string str){
  for(int k=0; k<str.size(); k++){
    Serial.write(str[k]);
  }
  // Serial.write("\n");
  delay(50);
}

inline void room_scan(){
  for(int pos=0; pos<FULL_SCAN; pos++){
    move_servo_to(pos);
    room_distances[pos] = read_distance();
  }
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

inline void send_sys_metrics(){
  string tmp_str = "sys_speed = " + std::to_string(sys_speed) + "\n";
  tmp_str += "sys_max_angle = " + std::to_string(sys_max_angle) + "\n";
  tmp_str += "sys_min_angle = " + std::to_string(sys_min_angle) + "\n";
  tmp_str += "sys_max_dist = " + std::to_string(sys_max_dist) + "\n";
  tmp_str += "sys_min_dist = " + std::to_string(sys_min_dist) + "\n";
  tmp_str += "sys_start_cmd = " + std::to_string(sys_start_cmd) + "\n";
  send_to_pc(tmp_str);
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
  // Combine bytes to form the integer
  sys_max_dist = (metrics[3] << 8) | metrics[4];
  sys_min_dist = (metrics[5] << 8) | metrics[6];
  sys_start_cmd = metrics[7];
}

inline void blink_times(int n){
  for(int ii=0; ii<n; ii++){
    digitalWrite(LED_BUILTIN, HIGH);
    delay(100);
    digitalWrite(LED_BUILTIN, LOW);
    delay(100);
  }
}

// builds a string in a format of xxx_yyy where xxx is the distance, yyy is the angle. Example: distance of 15 cm will be presented as 015 (with the leading zero)
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
  Serial.begin(BAUD_RATE); // Initializing serial port
  Serial.setTxBufferSize(BUFFER_SIZE);
  Serial.setRxBufferSize(BUFFER_SIZE);
  lidarSerial.begin(BAUD_RATE, SERIAL_8N1, RX_PIN, TX_PIN); // Initializing serial port
  servo_init();
  pinMode(LED_BUILTIN, OUTPUT);
  // flashlight init:
  pinMode(FLASHLIGHT_PIN, OUTPUT);
}

void loop() {
  // room_scan is the sys_start_cmd == 2.
  if(sys_start_cmd == 2){
    room_scan();    // updates the room_distances array with the room's measurements. 
    for(int i=0; i<FULL_SCAN; i++){
      last_scan[i] = room_distances[i];
    }
    send_to_pc(ROOM_SCAN_DONE_SIGNAL);
    sys_start_cmd = 0;  // move to "standby" mode
  }
  if(sys_start_cmd == 0){
    digitalWrite(LED_BUILTIN, HIGH);
    while(Serial.available() == 0) {}
  } 
  if(sys_start_cmd == 1) { // we're on.
    blink_times(10);
    // sweep left
    int cur_dist;
    for(int pos=0; pos<=180; pos++){
      move_servo_to(pos);
      cur_dist = read_distance();   // in cm
      if(cur_dist > sys_min_dist && cur_dist < sys_max_dist){
        string tmp_str = build_string(cur_dist, pos);
        send_to_pc(tmp_str);
        // auxiliary logic, turn on the flash light when the distance is above 100cm.
        // if(cur_dist > 100){
        //   digitalWrite(FLASHLIGHT_PIN, HIGH);
        // } else {
        //   digitalWrite(FLASHLIGHT_PIN, LOW);
        // }
      }
    }
    // sweep right.
    for(int pos=180; pos>=0; pos--){
      move_servo_to(pos);
      cur_dist = read_distance();   // in cm
      if(cur_dist > sys_min_dist && cur_dist < sys_max_dist){
        string tmp_str = build_string(cur_dist, pos);
        send_to_pc(tmp_str);
        // auxiliary logic, turn on the flash light when the distance is above 100cm.
        // if(cur_dist > 100){
        //   digitalWrite(FLASHLIGHT_PIN, HIGH);
        // } else {
        //   digitalWrite(FLASHLIGHT_PIN, LOW);
        // }
      }
    }
  }
  if(Serial.available() > 0) { // Check if new data is available to read
    delay(100); // wait for all of the information to arrive by serial communication.
    Serial.readBytes(metrics, NUM_OF_PC_INPUTS);
    update_sys_metrics();
    blink_times(3);
    string str = "recieved new metrics!";
    send_to_pc(str);
    // print_sys_metrics();
    delay(100);
  }
}
