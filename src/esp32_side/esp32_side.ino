#include <HardwareSerial.h>  // Reference the ESP32 built-in serial port library
#include <string>
#include <vector>
#include <algorithm>

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

inline int get_most_common_dist(std::vector<int>& vec){
  sort(vec.begin(), vec.end());
  int c=0; 
  uint16_t prev = -1;
  int max_c = 0;
  int max_val = 0;
  for(auto x: vec){
    if(prev == -1){
      prev = x;
      continue;
      c=1;
    }
    if(x==prev){
      c++;
      if(max_c < c){
        max_c = c;
        max_val = x;
      }
    } else {
      prev = x;
      c=1;
    }
  }
  return max_val;
}

inline void read_and_send_distance() {
  std::vector<int> vec(10);
  uint8_t buf[9] = { 0 };  // An array that holds data
  if (lidarSerial.available() > 0) {
    lidarSerial.readBytes(buf, 9);           // Read 9 bytes of data
    if (buf[0] == 0x59 && buf[1] == 0x59) {  // lidar packet header
      uint16_t distance = buf[2] + buf[3] * 256;
      if (distance > LIDAR_MAX_READ_DISTANCE) distance = 0;
      vec.push_back(int(distance));
      // uint16_t strength = buf[4] + buf[5] * 256;
      // int16_t temperature = buf[6] + buf[7] * 256;
      // TODO: if signal strenth is below 100 then the reading is unreliable!
      //TODO: add basic weighting system to determine the true distance from an object
      if (counter > 10) {  // sends the 10th reading only, to slow down the buffer filling rate
        // uint16_t common_dist = get_most_common_dist(vec);
        // string comm_dist_str = std::to_string(common_dist);
        string dist_str = std::to_string(distance);
        while(dist_str.size() < 3){
          dist_str = "0" + dist_str;
        }
        for (int i = 0; i < dist_str.size(); i++) {
          Serial.write(dist_str[i]);
        }
        // while(comm_dist_str.size() < 3){
        //   comm_dist_str = "0" + comm_dist_str;
        // }
        // for (int i = 0; i < comm_dist_str.size(); i++) {
        //   Serial.write(comm_dist_str[i]);
        // }
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