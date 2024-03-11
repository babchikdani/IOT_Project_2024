import serial
import time

# The metrics format:
# uint8_t sys_speed;     // metrics[0]
# uint8_t sys_max_angle; // metrics[1], in degrees.
# uint8_t sys_min_angle; // metrics[2], in degrees.
# uint8_t sys_max_dist;  // metrics[3], in meters.
# uint8_t sys_min_dist;  // metrics[4], in meters.
# uint8_t sys_start_cmd; // metrics[5], 1 to start. 0 to stop.

# Establish a connection to the COM port the ESP32 is connected to
ser = serial.Serial('COM5', 115200)  # Replace 'COM_PORT' with the correct port


# define the metrics.
speed = 1
max_angle = 90   # in degrees
min_angle = 0       # in degrees
max_dist = 7        # in meters
min_dist = 1        # in meters
start_cmd = 1       # 1 start, 0 stop.
metrics = [speed, max_angle, min_angle, max_dist, min_dist, start_cmd]
bytes_to_send = bytearray(metrics)

# Send data
# ser.flush()
ser.write(bytes_to_send)

# Wait for a response and read it
time.sleep(1)

while True:
    time.sleep(1)
    if ser.in_waiting > 0:
        incoming_data = ser.read(ser.in_waiting)
        print(time.time(), ' Received:', incoming_data.decode())
    else:
        print(time.time(), 'Nada')



