#include <Servo.h>

Servo myservo;
int servoPin = 9;

int flag = 0;

inline void move_servo_to(int pos) {
  myservo.write(pos);
  delay(15);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  myservo.attach(servoPin);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  if (!flag) {
    while (Serial.available() < 8) {}
    char buf[8] = { 0 };
    Serial.readBytes(buf, 8);
    if (buf[7] == 2) {  // recieved room scan signal
      String rec_str = "rec_sig\n";
      for (int k = 0; k < rec_str.length(); k++) {
        Serial.write(rec_str[k]);
      }
      flag = 1;
    } else {
        while (1) {  // error - room scan value was wrong!!!
          digitalWrite(LED_BUILTIN, HIGH);
          delay(500);
          digitalWrite(LED_BUILTIN, LOW);
          delay(500);
        }
    }

  } else {
    // put your main code here, to run repeatedly:
    for (int pos = 0; pos <= 180; pos++) {
      move_servo_to(pos);
      String angle_str = String(pos) + "\n";
      for (int k = 0; k < angle_str.length(); k++) {
        Serial.write(angle_str[k]);
      }
      // wait for ack byte.
      while (Serial.available() < 1) {}
      // read the ack:
      char ack_buf[1] = { 0 };
      Serial.readBytes(ack_buf, 1);
      if (ack_buf[0] == 1) {  // recieved ack from PC
        continue;
      } else {
        while (1) {  // error - wrong value from ack recieved!
          digitalWrite(LED_BUILTIN, HIGH);
          delay(500);
          digitalWrite(LED_BUILTIN, LOW);
          delay(500);
        }
      }
    }
    // sweep right.
    for (int pos = 180; pos >= 0; pos--) {
      move_servo_to(pos);
      String angle_str = String(pos) + "\n";
      for (int k = 0; k < angle_str.length(); k++) {
        Serial.write(angle_str[k]);
      }
      while (Serial.available() < 1) {}
      char ack_buf[1] = { 0 };
      Serial.readBytes(ack_buf, 1);
      if (ack_buf[0] == 1) {  // recieved ack from PC
        continue;
      } else {
        while (1) {  // error - check the led
          digitalWrite(LED_BUILTIN, HIGH);
          delay(100);
          digitalWrite(LED_BUILTIN, LOW);
          delay(100);
        }
      }
    }
  }
}
