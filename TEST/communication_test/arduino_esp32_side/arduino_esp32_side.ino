#include <HardwareSerial.h>

#define BUILTIN_LED 13
HardwareSerial SerialPort(2); // use UART2

void setup() {
  // put your setup code here, to run once:
  SerialPort.begin (115200, SERIAL_8N1, 3, 1);
  // SerialPort.print("Serial port was initialized")
  pinMode(BUILTIN_LED, OUTPUT);

  SerialPort.print(1); // handshake message
}

void loop() {
  // put your main code here, to run repeatedly:
  int read_val = SerialPort.read();
  SerialPort.print(1); // Acceptance message
  digitalWrite(BUILTIN_LED, LOW);
  delay(500);
  digitalWrite(BUILTIN_LED, HIGH);
  delay(500);
  digitalWrite(BUILTIN_LED, LOW);
  delay(5000);
  read_val = SerialPort.read();
  SerialPort.print(1); // Acceptance message
  digitalWrite(BUILTIN_LED, LOW);
  delay(500);
  digitalWrite(BUILTIN_LED, HIGH);
  delay(500);
  digitalWrite(BUILTIN_LED, LOW);
  delay(500);
  digitalWrite(BUILTIN_LED, HIGH);
  delay(500);
  digitalWrite(BUILTIN_LED, LOW);
  delay(5000);
  read_val = SerialPort.read();
  SerialPort.print(1); // Acceptance message
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
  delay(5000);

  SerialPort.print(1);
  SerialPort.read();
  delay(5000);
  SerialPort.print(2);
  SerialPort.read();
  delay(5000);
  SerialPort.print(3);
  SerialPort.read();
  delay(5000);
}
