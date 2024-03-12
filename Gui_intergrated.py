import tkinter
import tkinter as tk
import math
import serial
import time

from tkinter import messagebox



RADAR_WIDTH = 800
RADAR_HEIGHT = 400
CENTER_X = RADAR_WIDTH/2
CENTER_Y = 400
LINE_LENGTH = 400
BAUD_RATE = 115200
ser = serial.Serial('COM5', BAUD_RATE)  # Change 'COMX' to your ESP32's UART port

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

        self.max_angle_label = tk.Label(root, text="Maximum Scan Angle:")
        self.max_angle_scale = tk.Scale(root, from_=0, to=180, orient="horizontal", resolution=1)

        self.min_angle_label = tk.Label(root, text="Minimum Scan Angle:")
        self.min_angle_scale = tk.Scale(root, from_=0, to=180, orient="horizontal", resolution=1)

        self.max_dist_label = tk.Label(root, text="Maximum Scan Distance [cm]:")
        self.max_dist_scale = tk.Scale(root, from_=50, to=800, orient="horizontal", resolution=1)

        self.min_dist_label = tk.Label(root, text="Minimum Scan Distance [cm]:")
        self.min_dist_scale = tk.Scale(root, from_=50, to=800, orient="horizontal", resolution=1)

        self.start_button = tk.Button(root, text="Start Scan", command=self.start_scan, bg="green", width=20, height=2)
        self.stop_button = tk.Button(root, text="Stop Scan", command=self.stop_scan, bg="red", width=20, height=2)


        # Create a canvas for radar display
        self.radar_canvas = tk.Canvas(root, width=RADAR_WIDTH, height=RADAR_HEIGHT, bg="black")

        # Place UI elements on the grid
        pad_x = 3
        pad_y = 3
        self.speed_label.grid(row=0, column=0, padx=pad_x, pady=pad_y)
        self.speed_scale.grid(row=0, column=1, padx=pad_x, pady=pad_y)

        self.max_angle_label.grid(row=1, column=0, padx=pad_x, pady=pad_y)
        self.max_angle_scale.grid(row=1, column=1, padx=pad_x, pady=pad_y)

        self.min_angle_label.grid(row=2, column=0, padx=pad_x, pady=pad_y)
        self.min_angle_scale.grid(row=2, column=1, padx=pad_x, pady=pad_y)

        self.max_dist_label.grid(row=3, column=0, padx=pad_x, pady=pad_y)
        self.max_dist_scale.grid(row=3, column=1, padx=pad_x, pady=pad_y)

        self.min_dist_label.grid(row=4, column=0, padx=pad_x, pady=pad_y)
        self.min_dist_scale.grid(row=4, column=1, padx=pad_x, pady=pad_y)

        self.start_button.grid(row=5, column=0, columnspan=1, padx=pad_x, pady=pad_y)
        self.stop_button.grid(row=5, column=1, columnspan=3, padx=pad_x, pady=pad_y)

        self.radar_canvas.grid(row=6, column=0, columnspan=2, padx=pad_x, pady=pad_y)
        self.radar_canvas.create_text(40, 20, text="Standby", fill="green", font=("Arial", 8, "bold"),
                                      tags="standby")
        # Initialize radar scanning state
        self.scanning = False
        self.scan_direction = 1  # 1 for forward, -1 for reverse
        self.current_angle = 90
        x = CENTER_X + LINE_LENGTH * math.cos(math.radians(self.current_angle))
        y = CENTER_Y - LINE_LENGTH * math.sin(math.radians(self.current_angle))  # Adjusted for upper side
        self.radar_canvas.create_line(CENTER_X, CENTER_Y, x, y, fill="green1", width=1, tags="line")
        # Create arc for distance measuring.
        radius = 50
        delta = 50
        for i in range(8):
            self.radar_canvas.create_arc(CENTER_X - radius, CENTER_Y - radius,
                                         CENTER_X + radius, CENTER_Y + radius,
                                         start=0, extent=180, outline="green", width=1, style=tk.ARC, tags=f"{i}m")
            radius = radius + delta
            # write distance to the arcs
            self.radar_canvas.create_text(CENTER_X, 500-radius-5, text=f"{i}m", fill="green", font=("Arial", 8, "bold"))

    
    def read_uart(self):
        if ser.in_waiting > 0:
            # Read the response
            # for item in self.getstrings(ser):
            #     print(item)
            incoming_data = ser.read(7).decode()
            # ser.flushInput()
            # time.sleep(0.5)
            # ser.flushOutput()
            
            # dist, self.current_angle = incoming_data.split('_')
            self.current_angle = int(incoming_data.split('_')[1])
            return int(incoming_data.split('_')[0])
        
        return 0

    def check_user_input(self):
        if self.min_angle_scale.get() > self.max_angle_scale.get():
            tk.messagebox.showwarning("Warning", "Minimum Angle cannot be larger than Maximum Angle")
            return 1
        if self.min_dist_scale.get() > self.max_dist_scale.get():
            tk.messagebox.showwarning("Warning", "Minimum Scan Distance cannot be larger than Maximum Scan "
                                                 "Distance")
            return 1
        return 0


    def disable_scales(self):
        self.max_dist_scale.configure(state='disabled')
        self.min_dist_scale.configure(state='disabled')
        self.max_angle_scale.configure(state='disabled')
        self.min_angle_scale.configure(state='disabled')
        self.speed_scale.configure(state='disabled')

    def enable_scales(self):
        self.max_dist_scale.configure(state='active')
        self.min_dist_scale.configure(state='active')
        self.max_angle_scale.configure(state='active')
        self.min_angle_scale.configure(state='active')
        self.speed_scale.configure(state='active')

    def start_scan(self):
        if self.check_user_input() == 1:
            return
        if not self.scanning:
            # Start radar scanning logic here
            print("Radar scanning started.")
            self.disable_scales()
            self.scanning = True
            self.update_radar_display()
            self.current_angle += 1
            self.radar_canvas.delete("standby")
            self.radar_canvas.create_text(40, 20, text="Scanning", fill="green", font=("Arial", 8, "bold"),
                                          tags="scanning")

    def stop_scan(self):
        if self.scanning:
            # Stop radar scanning logic here
            print("Radar scanning stopped.")
            self.enable_scales()
            self.scanning = False
            self.update_radar_display()
            self.radar_canvas.delete("scanning")
            self.radar_canvas.create_text(40, 20, text="Standby", fill="green", font=("Arial", 8, "bold"),
                                          tags="standby")

    def update_radar_display(self):
        if self.scanning:
            # Simulate radar scan motion (single sweep line)
            dist = self.read_uart()
            if int(dist) > 0:
                print(f"Found object in dist:{dist}, and angle:{self.current_angle}")

            x = CENTER_X + LINE_LENGTH * math.cos(math.radians(self.current_angle))
            y = CENTER_Y - LINE_LENGTH * math.sin(math.radians(self.current_angle))  # Adjusted for upper side
            self.radar_canvas.delete("line")  # Clear previous line
            self.radar_canvas.create_line(CENTER_X, CENTER_Y, x, y, fill="green1", width=1, tags="line")
            self.root.update()  # Update the display
            self.root.after(1, self.update_radar_display)  # Recursive call for animation

        # send_metrics()  # try to send


if __name__ == "__main__":
    root = tk.Tk()
    app = RadarControlApp(root)
    root.mainloop()