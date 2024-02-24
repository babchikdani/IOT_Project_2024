#include <HardwareSerial.h>
LED = 13

void setup() {
  HardwareSerial SerialPort(2); // use UART2
  // put your setup code here, to run once:
  SerialPort.begin (115200, SERIAL_8N1, 3, 1);

  pinMode(BUILTIN_LED, OUTPUT);
  int read_val = SerialPort.read();
  digitalWrite(BUILTIN_LED, LOW);
  delay(500);
  digitalWrite(BUILTIN_LED, HIGH);
  delay(500);
  digitalWrite(BUILTIN_LED, LOW);
  delay(5000);
  int read_val = SerialPort.read();
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
  int read_val = SerialPort.read();
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
  delay(5000);
  SerialPort.print(2);
  delay(5000);
  SerialPort.print(3);
}

void loop() {
  // put your main code here, to run repeatedly:

}
