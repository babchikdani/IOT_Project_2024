import tkinter as tk
import math
import numpy as np
import serial
import time


ser = serial.Serial('COM5', 115200)  # Change 'COMX' to your ESP32's UART port

ser.flushInput()
ser.flushOutput()

def send_metrics(speed=1, min_angle=0, max_angle=180, min_dist=1, max_dist=8, start_stop=1):
    byte_array = [speed, min_angle, max_angle, min_dist, max_dist, start_stop]
    data_to_send = bytes(byte_array)
    while True:
        ser.write(data_to_send)
        print(f'{time.time()}, Data sent successfully.')
        time.sleep(0.5)

        # Check if there's any response from the device
        if ser.in_waiting > 0:
            # Read the response
            response = ser.readline().strip()
            print("Received:", response)

            # Process the response here
            # Example: If response is 'OK', break the loop
            if response != '':
                print("Received confirmation. Exiting loop.")
                break


class RadarControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Radar Control")

        # Create UI elements
        self.speed_label = tk.Label(root, text="Speed:")
        self.speed_scale = tk.Scale(root, from_=1, to=3, orient="horizontal")

        self.angle_label = tk.Label(root, text="Angle Restriction:")
        self.angle_scale = tk.Scale(root, from_=0, to=180, orient="horizontal")

        self.start_button = tk.Button(root, text="Start Scan", command=self.start_scan)
        self.stop_button = tk.Button(root, text="Stop Scan", command=self.stop_scan)

        # Create a canvas for radar display
        self.radar_canvas = tk.Canvas(root, width=300, height=300, bg="black")

        # Place UI elements on the grid
        self.speed_label.grid(row=0, column=0, padx=10, pady=10)
        self.speed_scale.grid(row=0, column=1, padx=10, pady=10)

        self.angle_label.grid(row=1, column=0, padx=10, pady=10)
        self.angle_scale.grid(row=1, column=1, padx=10, pady=10)

        self.start_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        self.stop_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.radar_canvas.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Initialize radar scanning state
        self.scanning = False
        self.scan_direction = 1  # 1 for forward, -1 for reverse
        self.current_angle = 90
        x = 150 + 120 * math.cos(math.radians(self.current_angle))
        y = 150 - 120 * math.sin(math.radians(self.current_angle))  # Adjusted for upper side
        self.radar_canvas.create_line(150, 150, x, y, fill="green", width=2, tags="line")
    
    def read_uart(self):
        if ser.in_waiting > 0:
            # Read the response
            # for item in self.getstrings(ser):
            #     print(item)
            incoming_data = ser.read(ser.in_waiting)
            print('Received:', incoming_data.decode())
        
    def getstrings(self, port):
        buf = bytearray()
        while True:
            b = port.read(1)
            if b == b'\x02':
                del buf[:]
            elif b == b'\x03':
                yield buf.decode('ascii')
            else:
                buf.append(b)
    
    def start_scan(self):
        if not self.scanning:
            # Start radar scanning logic here
            print("Radar scanning started.")
            self.scanning = True
            self.update_radar_display()
            
            self.current_angle += 1

    def stop_scan(self):
        if self.scanning:
            # Stop radar scanning logic here
            print("Radar scanning stopped.")
            self.scanning = False
            self.update_radar_display()

    def update_radar_display(self):
        if self.scanning:
            # Simulate radar scan motion (single sweep line)
            self.read_uart()

            x = 150 + 120 * math.cos(math.radians(self.current_angle))
            y = 150 - 120 * math.sin(math.radians(self.current_angle))  # Adjusted for upper side
            self.radar_canvas.delete("line")  # Clear previous line
            self.radar_canvas.create_line(150, 150, x, y, fill="green", width=2, tags="line")
            self.root.update()  # Update the display
            self.root.after(50, self.update_radar_display)  # Recursive call for animation

        # send_metrics()  # try to send


if __name__ == "__main__":
    root = tk.Tk()
    app = RadarControlApp(root)
    root.mainloop()
