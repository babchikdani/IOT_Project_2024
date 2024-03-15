#include <HardwareSerial.h>  // Reference the ESP32 built-in serial port library
#include <string.h>

using std::string;

HardwareSerial lidarSerial(2);  // Using serial port 2
#define RXD2 16                 // green TFMini-S wire
#define TXD2 17                 // white TFMini-S wire

int counter = 0;
int flag = 0;

void setup() {  // Initializing serial port
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.begin(115200);
}

void loop() {
  if (!flag) {
    while (Serial.available() < 1) {}
    uint8_t buf = 0;
    Serial.readBytes(&buf, 1);
    if (buf == 2) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(1000);
    }
    flag = 1;
    lidarSerial.begin(115200, SERIAL_8N1, RXD2, TXD2);  // Initializing serial port
  }
  uint8_t buf[9] = { 0 };  // An array that holds data
  if (lidarSerial.available() > 0) {
    lidarSerial.readBytes(buf, 9);  // Read 9 bytes of data
    if (buf[0] == 0x59 && buf[1] == 0x59) {
      uint16_t distance = buf[2] + buf[3] * 256;
      if (distance > 10000) distance = 0;
      uint16_t strength = buf[4] + buf[5] * 256;
      int16_t temperature = buf[6] + buf[7] * 256;
      if (counter > 10) {
        string dist_str = std::to_string(distance) + "\n";
        for (int k = 0; k < dist_str.size(); k++) {
          Serial.write(dist_str[k]);
        }
        counter = 0;
      }
      counter++;
    }
  }
  delay(10);
}