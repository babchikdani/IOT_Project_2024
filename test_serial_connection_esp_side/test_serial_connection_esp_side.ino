
uint8_t arr[7] = {1, 2, 3, 4, 5, 6, 7}; 

void setup() {
  Serial.begin(115200); // Start the serial communication at 115200 baud rate
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.flush();
}

void loop() {
  // we recieve values different than 1, 2, 3, 4, 5, 6, 7
    if(Serial.available()) { // Check if data is available to read
      Serial.readBytes(arr, 7);
      for(int i=0; i<7; i++){
        arr[i] = arr[i] + 5;
        Serial.write(arr[i]);
      }
    }
}


