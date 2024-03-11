#include <HardwareSerial.h> // Reference the ESP32 built-in serial port library
#include <ESP32Servo.h>

Servo myservo;
int servoPin = 15;

HardwareSerial lidarSerial(2); // Using serial port 2

#define RXD2 13
#define TXD2 12
#define SERVO_MIN_PWM 544
#define SERVO_MAX_PWM 2400



inline void move_servo_to(int pos){
  myservo.write(pos);
  delay(15);
}


inline void servo_init(){
    ESP32PWM::allocateTimer(0);
	  ESP32PWM::allocateTimer(1);
	  ESP32PWM::allocateTimer(2);
	  ESP32PWM::allocateTimer(3);
	  myservo.setPeriodHertz(50);    // standard 50 hz servo
	  myservo.attach(servoPin, SERVO_MIN_PWM, SERVO_MAX_PWM); // attaches the servo on pin 18 to the servo object
}

void setup() {
  Serial.begin(115200); // Initializing serial port
  lidarSerial.begin(115200, SERIAL_8N1, RXD2, TXD2); // Initializing serial port for lidar.
  servo_init();
}

void loop() {
      uint16_t cur_dist;
      // sweep left
      for(int pos=0; pos<=180; pos=pos++){
        move_servo_to(pos);
        uint8_t buf[9] = {0}; // An array that holds data
        if (lidarSerial.available() > 0) {
          lidarSerial.readBytes(buf, 9); // Read 9 bytes of data
          if( buf[0] == 0x59 && buf[1] == 0x59)
          {
            uint16_t distance = buf[2] + buf[3] * 256;
            uint16_t strength = buf[4] + buf[5] * 256;
            int16_t temperature = buf[6] + buf[7] * 256;
            Serial.print("Distance: ");
            Serial.println(distance);
            // Serial.print(" cm, strength: ");
            // Serial.print(strength);
            // Serial.print(", temperature: ");
            // Serial.println(temperature / 8.0 - 256.0);
          }
        }
        delay(100); 
      }
      // sweep right
      for(int pos=180; pos>=0; pos=pos--){
        move_servo_to(pos);
        uint8_t buf[9] = {0}; // An array that holds data
      if (lidarSerial.available() > 0) {
        lidarSerial.readBytes(buf, 9); // Read 9 bytes of data
        if( buf[0] == 0x59 && buf[1] == 0x59)
        {
          uint16_t distance = buf[2] + buf[3] * 256;
          uint16_t strength = buf[4] + buf[5] * 256;
          int16_t temperature = buf[6] + buf[7] * 256;
          Serial.print("Distance: ");
          Serial.println(distance);
          // Serial.print(" cm, strength: ");
          // Serial.print(strength);
          // Serial.print(", temperature: ");
          // Serial.println(temperature / 8.0 - 256.0);
        }
      }
      delay(100); 
    }
}