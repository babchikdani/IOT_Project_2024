#include <ESP32Servo.h>


Servo myservo;
int servoPin = 15;

#define SERVO_MIN_PWM 544
#define SERVO_MAX_PWM 2400

inline void move_servo_to(int pos){
  myservo.write(pos);
  delay(15);
}

void setup() {
  // servo init:
  ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	myservo.setPeriodHertz(50);    // standard 50 hz servo
	myservo.attach(servoPin, SERVO_MIN_PWM, SERVO_MAX_PWM); // attaches the servo on pin 18 to the servo object
}

void loop() {
  // put your main code here, to run repeatedly:
  for(int pos=0; pos<=180; pos++){
    move_servo_to(pos);
  }
  for(int pos=180; pos>=0; pos--){
    move_servo_to(pos);
  }
}