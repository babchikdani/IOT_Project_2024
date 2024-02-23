"""
https://microcontrollerslab.com/esp32-uart-communication-pins-example/
"""

from machine import UART, Pin
from time import sleep

# Initialize serial communication with PC
uart = UART(0, baudrate=9600, tx=Pin(1), rx=Pin(3))

print("Starts Reading")
read_val = uart.readline().decode().strip()
assert read_val == 1, "Incorrect read value"
sleep(5)
read_val = uart.readline().decode().strip()
assert read_val == 2, "Incorrect read value"
sleep(5)
read_val = uart.readline().decode().strip()
assert read_val == 3, "Incorrect read value"
print("Finished reading\n")

print("Starts writing")
uart.write("Number 1:{}\n".format(1).encode())
sleep(5)
uart.write("Number 2:{}\n".format(2).encode())
sleep(5)
uart.write("Number 3:{}\n".format(3).encode())
print("Finished writing\n")
