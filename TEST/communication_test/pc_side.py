print("################## UART communication test ##################")

print("Imports serial lib")
import serial
print("Imports time lib")
from time import sleep

print("Initialize serial communication with ESP32")
ser = serial.Serial('COM3', 9600)  # Change 'COMX' to your ESP32's UART port

print("Waiting for handshake with ESP32")
ser.read()
print("Connection received\n")

if __name__ == "__main__":
    print("Starts writing")
    ser.write(1)
    ser.read() # Gets a message from ESP32 if the message was delivered
    print("--- Wrote 1 to ESP32... waiting for 5 seconds")
    sleep(5)
    ser.write(2)
    ser.read() # Gets a message from ESP32 if the message was delivered
    print("--- Wrote 2 to ESP32... waiting for 5 seconds")
    sleep(5)
    ser.write(3)
    ser.read() # Gets a message from ESP32 if the message was delivered
    print("--- Wrote 3 to ESP32... waiting for 5 seconds")
    print("Finished writing\n")

    print("Starts Reading")
    read_val = ser.read()
    ser.write(1)
    print(f"--- Value {read_val} was read(expecting-1)... waiting for 5 seconds")
    assert read_val == 1, "Incorrect read value"
    sleep(5)
    read_val = ser.read()
    ser.write(1)
    print(f"--- Value {read_val} was read(expecting-2)... waiting for 5 seconds")
    assert read_val == 2, "Incorrect read value"
    sleep(5)
    read_val = ser.read()
    ser.write(1)
    print(f"--- Value {read_val} was read(expecting-3)... waiting for 5 seconds")
    print("Finished reading\n")


print("############## UART communication test - done ###############")