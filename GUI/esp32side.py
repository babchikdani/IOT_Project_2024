from machine import UART, Pin
from time import sleep
from servo import Servo

# Define servo control pin
servo_pin = 2  # Example PWM Pin 2

# Define TFMiniS Lidar sensor UART pins
lidar_rx_pin = 16  # Example UART RX Pin 16
lidar_tx_pin = 17  # Example UART TX Pin 17

# Initialize servo
myServo = Servo(servo_pin)

# Initialize TFMiniS Lidar sensor serial communication
lidar_uart = UART(1, baudrate=115200, tx=Pin(lidar_tx_pin), rx=Pin(lidar_rx_pin), timeout=1000)

# Initialize serial communication with PC
uart = UART(0, baudrate=9600, tx=Pin(1), rx=Pin(3))


def change_degree_limitation(new_limit):
    # Function to change degree limitation
    # Implement your logic here
    pass


while True:
    # Read data from PC
    if uart.any():
        command = uart.readline().decode().strip()
        if command.startswith("set_degree_limit:"):
            new_limit = int(command.split(":")[1])
            change_degree_limitation(new_limit)
            uart.write("Degree limit set to {}\n".format(new_limit))

    # Read Lidar data
    if lidar_uart.any():
        header1 = lidar_uart.read(1)
        header2 = lidar_uart.read(1)

        if header1 == b'\x59' and header2 == b'\x59':
            data = lidar_uart.read(7)
            distance = data[0] + (data[1] << 8)
            strength = data[2] + (data[3] << 8)

            # Print Lidar data to serial monitor
            print("Distance: {} cm, Strength: {}".format(distance, strength))

    # Rotate servo from 0 to 180 degrees
    for angle in range(0, 181):
        myServo.write_angle(angle)
        sleep(0.015)  # Adjust delay as per your servo motor specifications

        # Send servo angle to PC through UART
        uart.write("Servo Angle: {}\n".format(angle))

    # Rotate servo from 180 to 0 degrees
    for angle in range(180, -1, -1):
        myServo.write_angle(angle)
        sleep(0.015)  # Adjust delay as per your servo motor specifications

        # Send servo angle to PC through UART
        uart.write("Servo Angle: {}\n".format(angle))