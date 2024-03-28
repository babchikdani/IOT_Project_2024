#include <Servo.h>

// commands:
#define OFF 0
#define ON 1
#define CONTINUE 2
#define RESET 3
#define MOVE_TO_ANGLE 4

// Sizes
#define INPUT_BYTES 7
#define ACK_SIZE 1
#define ACK 1
#define BUFFER_SIZE 7
#define LASER_PIN 13

// Servo defines
#define MIN_PWM 544
#define MAX_PWM 2400

Servo myservo;
int servoPin = 9;

uint8_t sys_speed = 1;
uint8_t sys_max_angle = 180;
uint8_t sys_min_angle = 0;
uint8_t sys_cmd = OFF;
uint8_t sys_ack = 0;
uint8_t sys_reset = 0; 
uint8_t sys_target_angle = 0;
uint8_t buf[BUFFER_SIZE] = { 0 };
int initial_room_scan_done = 0;

inline void move_servo_to(int pos) {
  myservo.write(pos);
  delay(60 - (15 * sys_speed));
}

inline void update_sys_metrics() {
  sys_speed = buf[0];
  sys_max_angle = buf[1];
  sys_min_angle = buf[2];
  if(buf[3] != CONTINUE){
    sys_cmd = buf[3];
  }
  sys_ack = buf[4];
  sys_reset = buf[5];
  sys_target_angle = buf[6];
}

inline void blink_forver() {
  while (1) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
  }
}

inline void send_angle_to_pc(uint8_t pos) {
  // send angle string to the PC
  Serial.write(pos);
  // Serial.write('\n');
}

inline void empty_serial_buffer() {
  while (Serial.available() > 0) {
    Serial.read();
  }
}

inline void wait_for_angle_ack() {
  while (Serial.available() < INPUT_BYTES) {}
  uint8_t old_sys_cmd = sys_cmd;
  // read the ack:
  Serial.readBytes(buf, INPUT_BYTES);
  update_sys_metrics(); // updates the sys_ack
  if(sys_cmd == OFF && old_sys_cmd == ON){

  }
  // else if (sys_ack != ACK) {  // didn't recieved ack from PC!
  //   blink_forver();      // system error.
  // }
}

inline void initial_room_scan() {
  digitalWrite(LED_BUILTIN, HIGH);
  for (uint8_t i = 0; i <= 180; i++) {
    move_servo_to(i);
    send_angle_to_pc(i);
    wait_for_angle_ack();
  }
  initial_room_scan_done = 1;
  digitalWrite(LED_BUILTIN, LOW);
  // sys_cmd = OFF;
}

void setup() {
  Serial.begin(115200);
  myservo.attach(servoPin, MIN_PWM, MAX_PWM);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LASER_PIN, OUTPUT);
  digitalWrite(LASER_PIN, LOW);
  digitalWrite(LED_BUILTIN, LOW);
  empty_serial_buffer();
}

void loop() {
  if (sys_cmd == ON) {
    digitalWrite(LED_BUILTIN, HIGH);
    // sweep left:
    for (int pos = 0; pos <= 180 && sys_cmd == ON; pos++) {
      move_servo_to(pos);
      send_angle_to_pc((uint8_t)pos);
      wait_for_angle_ack();
    }
    // sweep right:
    for (int pos = 180; pos >= 0 && sys_cmd == ON; pos--) {
      move_servo_to(pos);
      send_angle_to_pc((uint8_t)pos);
      wait_for_angle_ack();
    }
  }
  if (sys_cmd == OFF) {
    digitalWrite(LED_BUILTIN, LOW);
    while (Serial.available() < INPUT_BYTES) {} // wait for new command.
  }
  if(sys_cmd == MOVE_TO_ANGLE){
    move_servo_to(sys_target_angle);
    digitalWrite(LASER_PIN, HIGH);
    delay(1000);
    digitalWrite(LASER_PIN, LOW);
    sys_cmd = OFF;
  }
  if (Serial.available() >= INPUT_BYTES) {  // read new metrics
    Serial.readBytes(buf, BUFFER_SIZE);
    update_sys_metrics();
    if(sys_reset == 1){
      initial_room_scan_done = 0;
      sys_reset = 0;
    }
    if(initial_room_scan_done == 0) {
      initial_room_scan();
      while (Serial.available() < INPUT_BYTES) {} // wait for new command.
      Serial.readBytes(buf, BUFFER_SIZE);
      update_sys_metrics();
    }
  }
}
