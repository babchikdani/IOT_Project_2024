#include <HardwareSerial.h> // Reference the ESP32 built-in serial port library
#include <ESP32Servo.h>


Servo myservo;
int servoPin = 15;
HardwareSerial lidarSerial(2);  // Using serial port 2
HardwareSerial guiSerial(0);    // command serial port
#define RXD2 13 // green TFMini-S wire
#define TXD2 12 // white TFMini-S wire
#define SERVO_MIN_PWM 544
#define SERVO_MAX_PWM 2400
#define STOP 0
#define START 1
#define BAD_READ (-1)
#define LiDAR_MIN_SIGNAL_STRENGTH 100 
#define LiDAR_MIN_DISTANCE 30 // in cm
#define INT_MAX 2147483647
#define UINT16_T_MAX 65535

uint8_t user_input_speed;
uint8_t user_input_max_angle, user_input_min_angle; // in degrees 
uint8_t user_input_max_dist, user_input_min_dist; // in cm
uint8_t start_stop; // 1 - start. 0 - stop.
uint8_t sweep_delay; 


void setup() {
  //TF mini config:
  Serial.begin(115200); // Initializing serial port
  lidarSerial.begin(115200, SERIAL_8N1, RXD2, TXD2); // Initializing serial port
  guiSerial.begin(115200, SERIAL_8N1, 3, 1);
  // Servo config
  ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	myservo.setPeriodHertz(50);    // standard 50 hz servo
	myservo.attach(servoPin, SERVO_MIN_PWM, SERVO_MAX_PWM); // attaches the servo on pin 18 to the servo object

  pinMode(LED_BUILTIN, OUTPUT);

  // show where is the 0 and 180 degrees.
  myservo.write(0);
  delay(3000);
  myservo.write(180);
  delay(3000);
}

void loop() { 
  // initialize 
  uint8_t metrics[6] = {1, 0, 180, 50, 300, 1};
  guiSerial.flush();
  while(guiSerial.available()){
    delay(1);
  } // wait for gui information.
  guiSerial.readBytes(metrics, 6);
  user_input_speed = metrics[0];
  user_input_min_angle = metrics[1];
  user_input_max_angle = metrics[2];
  user_input_min_dist = metrics[3];
  user_input_max_dist = metrics[4];
  start_stop = metrics[5];
  sweep_delay = 15*(4-user_input_speed);
  
  // prints to Serial Monitor.
  // Serial.println(user_input_speed);
  // Serial.println(user_input_max_angle);
  // Serial.println(user_input_min_angle);
  // Serial.println(user_input_max_dist);
  // Serial.println(user_input_min_dist);
  // Serial.println(start_stop);



  uint16_t read_dist, object_min_dist;
  object_min_dist = UINT16_T_MAX;   // "Inifinity"
  int angle_at_min_dist = 0;
  // sweep right
	for (int pos = user_input_min_angle; pos <= user_input_max_angle; pos += 1) { // goes from 0 degrees to 180 degrees
		// in steps of 1 degree
		myservo.write(pos);    // tell servo to go to position in variable 'pos'
		delay(sweep_delay);             // waits 15ms for the servo to reach the position
    read_dist = readPrintDistanceAngle(pos);
    if(read_dist < object_min_dist && read_dist >= user_input_min_dist && read_dist <= user_input_max_dist && read_dist != BAD_READ){
      angle_at_min_dist = pos;
      object_min_dist = read_dist;
    }
	}
  // sweep left
	for (int pos = user_input_max_angle; pos >= user_input_min_angle; pos -= 1) { // goes from 180 degrees to 0 degrees
		myservo.write(pos);    // tell servo to go to position in variable 'pos'
		delay(sweep_delay);    
    read_dist = readPrintDistanceAngle(pos);
    if(read_dist < object_min_dist && read_dist >= user_input_min_dist && read_dist <= user_input_max_dist && read_dist != BAD_READ){
      angle_at_min_dist = pos;
      object_min_dist = read_dist;
    }
	}
  turnToMinAngle(angle_at_min_dist, object_min_dist);
}


inline void turnToMinAngle(int min_angle, int min_dist){
  myservo.write(min_angle);
  delay(15);
  Serial.print("\n-------------------------------------------\n");
  Serial.print("MININMUM DISTANCE: ");
  Serial.print(min_dist);
  Serial.print(", AT ANGLE: ");
  Serial.print(min_angle);
  Serial.print("\n-------------------------------------------\n");

  digitalWrite(BUILTIN_LED, HIGH);
  delay(500);
  digitalWrite(BUILTIN_LED, LOW);
  delay(500);
  digitalWrite(BUILTIN_LED, HIGH);
  delay(500);
  digitalWrite(BUILTIN_LED, LOW);
  delay(500);
  digitalWrite(BUILTIN_LED, HIGH);
  delay(500);
  digitalWrite(BUILTIN_LED, LOW);
  delay(500);
  digitalWrite(BUILTIN_LED, HIGH);
  delay(500);
  digitalWrite(BUILTIN_LED, LOW);
  delay(500);
}

// DONT CHANGE THE FOLLOWING CODE:
inline uint16_t readPrintDistanceAngle(int angle){
  uint16_t distance = 0;
  uint8_t buf[9] = {0}; // An array that holds data
  if (lidarSerial.available() > 0) {
    lidarSerial.readBytes(buf, 9); // Read 9 bytes of data
    if( buf[0] == 0x59 && buf[1] == 0x59)
    {
      distance = buf[2] + buf[3] * 256;
      uint16_t strength = buf[4] + buf[5] * 256;
      int16_t temperature = buf[6] + buf[7] * 256;
      if(strength <= LiDAR_MIN_SIGNAL_STRENGTH || distance <= LiDAR_MIN_DISTANCE){
        Serial.print("BAD READ\n");
        return BAD_READ;
      }
      // prints the data to the Serial Monitor
      Serial.print("Distance: ");
      Serial.print(distance);
      Serial.print(" cm, strength: ");
      Serial.print(strength);
      Serial.print(", angle: ");
      Serial.print(angle);
      Serial.println();
    }
  }
  delay(5); 
  return distance;
}

