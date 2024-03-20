import serial


esp32_serial = serial.Serial('COM5', 115200)  # Change 'COMX' to your ESP32's UART port
# esp32_serial.flushInput()
# esp32_serial.flushOutput()

if __name__ == "__main__":
    while True:
        if esp32_serial.in_waiting > 4:
            a = esp32_serial.readline()
            print('got raw:', a)
            print('got with decode:', a.decode())
            # print('got raw as int:', int(a))
            # print('got with decode as int:', int(a))
