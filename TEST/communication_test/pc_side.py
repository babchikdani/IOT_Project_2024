print("################## UART communication test ##################")

print("Imports serial lib")
import serial
print("Imports time lib")
from time import sleep

print("Initialize serial communication with ESP32")
ser = serial.Serial('UART0', 9600)  # Change 'COMX' to your ESP32's UART port


if __name__ == "__main__":
    print("Starts writing")
    ser.write("Number 1:{}\n".format(1).encode())
    print("--- Wrote 1 to ESP32... waiting for 5 seconds")
    sleep(5)
    ser.write("Number 2:{}\n".format(2).encode())
    print("--- Wrote 2 to ESP32... waiting for 5 seconds")
    sleep(5)
    ser.write("Number 3:{}\n".format(3).encode())
    print("--- Wrote 3 to ESP32... waiting for 5 seconds")
    print("Finished writing\n")

    print("Starts Reading")
    read_val = ser.readline().decode().strip()
    print(f"--- Value {read_val} was read(expecting-1)... waiting for 5 seconds")
    assert read_val == 1, "Incorrect read value"
    sleep(5)
    read_val = ser.readline().decode().strip()
    print(f"--- Value {read_val} was read(expecting-2)... waiting for 5 seconds")
    assert read_val == 2, "Incorrect read value"
    sleep(5)
    read_val = ser.readline().decode().strip()
    print(f"--- Value {read_val} was read(expecting-3)... waiting for 5 seconds")
    print("Finished reading\n")


print("############## UART communication test - done ###############")