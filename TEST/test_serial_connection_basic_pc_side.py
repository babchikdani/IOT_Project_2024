import serial
import time

# Establish a connection to the COM port the ESP32 is connected to
ser = serial.Serial('COM5', 115200)  # Replace 'COM_PORT' with the correct port

metrics = [10, 20, 30, 40, 50, 60, 70]
bytes_to_send = bytearray(metrics)

# Send data
ser.flush()
ser.write(bytes_to_send)

# Wait for a response and read it
time.sleep(1)
if ser.in_waiting > 0:
    incoming_data = ser.read(ser.in_waiting)
    for i in range(7):
        print('Received:', int(incoming_data[i]))

    ser.flush()

# Close the connection
ser.close()
