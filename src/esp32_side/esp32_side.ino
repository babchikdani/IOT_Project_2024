#include <HardwareSerial.h>  // Reference the ESP32 built-in serial port library
#include <string>

using std::string;


HardwareSerial lidarSerial(2);  // Using serial port 2
#define RXD2 16                 // green TFMini-S wire
#define TXD2 17                 // white TFMini-S wire
#define LIDAR_BAUD_RATE 115200
#define SERIAL_BAUD_RATE 115200
#define LIDAR_MAX_READ_DISTANCE 1200
#define ROOM_SCAN_CMD 2
#define ON 1
#define OFF 0

int lidar_serial_mode = OFF;
int counter = 0;
uint8_t cmd = OFF;

inline void blink_forever() {
  while (1) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
  }
}

inline void read_and_send_distance() {
  uint8_t buf[9] = { 0 };  // An array that holds data
  if (lidarSerial.available() > 0) {
    lidarSerial.readBytes(buf, 9);           // Read 9 bytes of data
    if (buf[0] == 0x59 && buf[1] == 0x59) {  // lidar packet header
      uint16_t distance = buf[2] + buf[3] * 256;
      if (distance > LIDAR_MAX_READ_DISTANCE) distance = 0;
      // uint16_t strength = buf[4] + buf[5] * 256;
      // int16_t temperature = buf[6] + buf[7] * 256;

      //TODO: add basic weighting system to determine the true distance from an object
      if (counter > 10) {  // sends the 10th reading only, to slow down the buffer filling rate
        string dist_str = std::to_string(distance);
        for (int i = 0; i < dist_str.size(); i++) {
          Serial.write(dist_str[i]);
        }
        Serial.write('\n');
        counter = 0;
      }
      counter++;
    } else {
      blink_forever();  // read corrupt lidar header
    }
  }
  delay(5);
}

inline void check_input(uint8_t in) {
  if (in != ON && in != OFF) {
    blink_forever();
  }
}

inline void empty_serial_buffer() {
  while (Serial.available() > 0) {
    Serial.read();
  }
}

inline void empty_lidar_serial_buffer() {
  while (lidarSerial.available() > 0) {
    lidarSerial.read();
  }
}

void setup() {  // Initializing serial port
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(SERIAL_BAUD_RATE);
}

void loop() {
  if (cmd == OFF) {
    digitalWrite(LED_BUILTIN, LOW);
    // empty_lidar_serial_buffer();
    // lidarSerial.end();
    lidar_serial_mode = OFF;
    while (Serial.available() < 1) {}
  }
  if (cmd == ON) {
    if (lidar_serial_mode == OFF) {
      digitalWrite(LED_BUILTIN, HIGH);
      lidarSerial.begin(LIDAR_BAUD_RATE, SERIAL_8N1, RXD2, TXD2);
      lidar_serial_mode = ON;
    }
    read_and_send_distance();
  }
  if (Serial.available() > 0) {
    uint8_t buf = 0;
    Serial.readBytes(&buf, 1);
    cmd = buf;
  }
}