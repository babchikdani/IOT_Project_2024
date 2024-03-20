import time
import tkinter as tk
import math
import serial
import array
import sys
from tkinter import messagebox

#TODO: instead of room scan, replace it with 'reset position or something' button which erases the radar
# canvas room visual data!

RADAR_WIDTH = 800
RADAR_HEIGHT = 400
CENTER_X = RADAR_WIDTH/2
CENTER_Y = 400
LINE_LENGTH = 400
BAUD_RATE = 115200
ROOM_SCAN_DONE_SIGNAL = "Room scan done!\n"
STOP_CMD = 0
START_CMD = 1
ROOM_SCAN_CMD = 2
DISTANCE_BYTES = 4
ANGLE_BYTES = 1
FULL_SCAN_DEGREES = 181
HIGH_SPEED = 3
MED_SPEED = 2
LOW_SPEED = 1




def send_metrics(speed=1, max_angle=180, min_angle=0, cmd=1, send_to_esp32=0, send_to_arduino=0, ack=0):
    # Send the data to the ESP32
    speed_byte = speed.to_bytes(1, 'little')
    min_angle_byte = min_angle.to_bytes(1, 'little')
    max_angle_byte = max_angle.to_bytes(1, 'little')
    cmd_byte = cmd.to_bytes(1, 'little')
    ack_byte = ack.to_bytes(1, 'little')
    if send_to_esp32:
        bytes_list_esp32 = [cmd_byte]
        data_to_send_esp32 = b''.join(bytes_list_esp32)
        esp32_serial.flushOutput()
        esp32_serial.write(data_to_send_esp32)
        print("Data was sent successfully to esp32")
    if send_to_arduino:
        bytes_list_arduino = [speed_byte, max_angle_byte, min_angle_byte, cmd_byte, ack_byte]
        data_to_send_arduino = b''.join(bytes_list_arduino)
        arduino_serial.flushOutput()
        arduino_serial.write(data_to_send_arduino)
        print("Data was sent successfully to arduino")


def send_ack(to_esp=0, to_arduino=0):
    ack = 1
    ack_byte = ack.to_bytes(1, 'little')
    bytes_list = [ack_byte]
    data_to_send = b''.join(bytes_list)
    if to_esp:
        # print('Send ACK to ESP32')
        esp32_serial.flushOutput()
        esp32_serial.write(data_to_send)
    if to_arduino:
        # print('Send ACK to Arduino')
        arduino_serial.flushOutput()
        arduino_serial.write(data_to_send)


def read_servo():
    while arduino_serial.in_waiting < ANGLE_BYTES:
        pass
    angle = int.from_bytes(arduino_serial.read(1), byteorder='little', signed=False)
    # if incoming_data[-1] == '\n':
    #     incoming_data = incoming_data[:-1]
    # if incoming_data[-1] == '\r':
    #     incoming_data = incoming_data[:-1]
    # print("incoming_data:", incoming_data)
    print('read_servo got:', angle)
    # print('as int is is', int(incoming_data))
    # angle = int(incoming_data)
    # print("angle:", angle)
    return angle


def read_lidar():
    # esp32_serial.flushOutput()
    # esp32_serial.flushInput()
    while esp32_serial.in_waiting < 4:
        # print('in read_lidar while loop')
        pass
    incoming_data = esp32_serial.readline().decode()
    # if incoming_data[-1] == '\n':
    #     incoming_data = incoming_data[:-1]
    # if incoming_data[-1] == '\r':
    #     incoming_data = incoming_data[:-1]
    dist = int(incoming_data)
    # print("dist:", dist)
    return dist






class RadarControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control")
        self.blip_id = 0
        self.first_scan = True
        self.room_scan_data = array.array('i', [0]*FULL_SCAN_DEGREES)

        # Create UI elements
        self.logo = tk.PhotoImage(file="../logo.png")
        self.resized_logo = self.logo.subsample(self.logo.width()//200, self.logo.height()//200)
        self.image_label = tk.Label(root, image=self.resized_logo)
        self.image_label.pack()
        self.label_font = ("Arial", 12, "normal")
        self.speed_label = tk.Label(root, text="Speed:", font=self.label_font)
        self.speed_scale = tk.Scale(root, from_=1, to=3, orient="horizontal")

        self.max_angle_label = tk.Label(root, text="Maximum Scan Angle:", font=self.label_font)
        self.max_angle_scale = tk.Scale(root, from_=0, to=180, orient="horizontal", resolution=1)
        self.max_angle_scale.set(180)

        self.min_angle_label = tk.Label(root, text="Minimum Scan Angle:", font=self.label_font)
        self.min_angle_scale = tk.Scale(root, from_=0, to=180, orient="horizontal", resolution=1)

        self.max_dist_label = tk.Label(root, text="Maximum Scan Distance [cm]:", font=self.label_font)
        self.max_dist_scale = tk.Scale(root, from_=50, to=800, orient="horizontal", resolution=1)
        self.max_dist_scale.set(800)

        self.min_dist_label = tk.Label(root, text="Minimum Scan Distance [cm]:", font=self.label_font)
        self.min_dist_scale = tk.Scale(root, from_=50, to=800, orient="horizontal", resolution=1)

        self.start_button = tk.Button(root, text="Start Scan", command=self.start_scan, bg="green", width=20, height=2,
                                      font=("Arial", 12, "italic"))
        self.stop_button = tk.Button(root, text="Stop Scan", command=self.stop_scan, bg="red", width=20, height=2,
                                     font=("Arial", 12, "italic"))
        self.reset_button = tk.Button(root, text="Reset", command=self.reset_scan, bg="blue", width=20, height=2,
                                      font=("Arial", 12, "italic"))

        # Create a canvas for radar display
        self.radar_canvas = tk.Canvas(root, width=RADAR_WIDTH, height=RADAR_HEIGHT, bg="black")

        # Place UI elements on the grid
        pad_x = 2
        pad_y = 2
        self.image_label.grid(row=0, column=2, padx=pad_x, pady=pad_y, rowspan=4)

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

        self.reset_button.grid(row=5, column=0, columnspan=1, padx=pad_x, pady=pad_y)

        self.start_button.grid(row=5, column=1, columnspan=1, padx=pad_x, pady=pad_y)
        self.stop_button.grid(row=5, column=2, columnspan=1, padx=pad_x, pady=pad_y)

        self.radar_canvas.grid(row=7, column=0, columnspan=3, padx=pad_x, pady=pad_y)
        self.radar_canvas.create_text(40, 20, text="Standby", fill="green", font=("Arial", 10, "bold"),
                                      tags="standby")
        # Initialize radar scanning state
        self.scanning = False
        self.scan_direction = 1  # 1 for forward, -1 for reverse
        self.current_angle = 90
        x = CENTER_X + LINE_LENGTH * math.cos(math.radians(self.current_angle))
        y = CENTER_Y - LINE_LENGTH * math.sin(math.radians(self.current_angle))  # Adjusted for upper side
        self.radar_canvas.create_line(CENTER_X, CENTER_Y, x, y, fill="green1", width=1, tags="line")
        # Create arcs for distance measuring.
        radius = 50
        delta = 50
        for i in range(8):
            self.radar_canvas.create_arc(CENTER_X - radius, CENTER_Y - radius,
                                         CENTER_X + radius, CENTER_Y + radius,
                                         start=0, extent=180, outline="green", width=1, style=tk.ARC, tags=f"{i}m")
            radius = radius + delta
            # write distance to the arcs
            self.radar_canvas.create_text(CENTER_X, 500-radius-5, text=f"{i}m", fill="green", font=("Arial", 8, "bold"))

    def check_scales_input(self):
        if self.min_angle_scale.get() > self.max_angle_scale.get():
            tk.messagebox.showwarning("Warning", "Minimum Angle cannot be larger than Maximum Angle")
            return 1
        if self.min_dist_scale.get() > self.max_dist_scale.get():
            tk.messagebox.showwarning("Warning", "Minimum Scan Distance cannot be larger than Maximum Scan "
                                                 "Distance")
            return 1    # 1 is error
        return 0  # 0 is success

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

    def draw_surroundings(self):
        for i in range(FULL_SCAN_DEGREES-1):
            if self.room_scan_data[i] == 0 or self.room_scan_data[i+1] == 0:
                continue  # skip.
            x0 = CENTER_X + self.room_scan_data[i] * math.cos(math.radians(i))/2
            y0 = CENTER_Y - self.room_scan_data[i] * math.sin(math.radians(i))/2
            x1 = CENTER_X + self.room_scan_data[i+1] * math.cos(math.radians(i+1))/2
            y1 = CENTER_Y - self.room_scan_data[i+1] * math.sin(math.radians(i+1))/2
            self.radar_canvas.create_line(x0, y0, x1, y1, fill="yellow", width=2, tags="surroundings")
            self.radar_canvas.update()

    def reset_scan(self):
        self.stop_scan()
        self.first_scan = True
        for i in range(FULL_SCAN_DEGREES):
            self.room_scan_data[i] = 0
        self.radar_canvas.delete("surroundings")


    def start_scan(self):
        # esp32_serial.flushInput()
        if self.check_scales_input() == 1:
            return
        if not self.scanning:
            self.disable_scales()
            self.scanning = True
            self.radar_canvas.delete("standby")
            self.radar_canvas.create_text(40, 20, text="Scanning", fill="green", font=("Arial", 10, "bold"),
                                          tags="scanning")
            self.radar_canvas.update()
            if self.first_scan:
                print("Initial room scan started.")
                self.radar_canvas.create_text(400, 200, text="Initial Room Scan", fill="wheat",
                                              font=("Arial", 50, "bold"), tags="initial_scanning")
                self.radar_canvas.update()
                send_metrics(speed=HIGH_SPEED, max_angle=int(self.max_angle_scale.get()),
                             min_angle=int(self.min_angle_scale.get()), send_to_arduino=1, send_to_esp32=1,
                             cmd=START_CMD)
                for i in range(FULL_SCAN_DEGREES):
                    self.current_angle = read_servo()
                    tmp_dist = read_lidar()
                    # get only good readings!
                    while tmp_dist == 0:
                        tmp_dist = read_lidar()
                    self.room_scan_data[i] = tmp_dist
                    print('at angle:', self.current_angle, 'distance:', self.room_scan_data[i])
                    send_ack(to_arduino=1)  # tell the arduino its ok to move
                # send_metrics(send_to_esp32=1, send_to_arduino=1, cmd=STOP_CMD)
                # esp32_serial.flushOutput()
                # esp32_serial.flushInput()
                self.first_scan = False
                self.radar_canvas.delete("initial_scanning")
                self.draw_surroundings()
                self.radar_canvas.update()
            # Start radar scanning logic here
            print("Radar scanning started.")
            send_metrics(speed=int(self.speed_scale.get()), max_angle=int(self.max_angle_scale.get()),
                         min_angle=int(self.min_angle_scale.get()), cmd=START_CMD, send_to_esp32=1, send_to_arduino=1)
            self.update_radar_display()

    def stop_scan(self):
        if self.scanning:
            # Stop radar scanning logic here
            send_metrics(cmd=STOP_CMD, send_to_arduino=1, send_to_esp32=1)
            print("Radar scanning stopped.")
            self.enable_scales()
            self.scanning = False
            self.update_radar_display()
            self.radar_canvas.delete("scanning")
            self.radar_canvas.create_text(40, 20, text="Standby", fill="green", font=("Arial", 10, "bold"),
                                          tags="standby")

    def update_radar_display(self):
        if self.scanning:
            # Simulate radar scan motion (single sweep line)
            print('request lidar')
            dist = read_lidar()
            print('request servo')
            while arduino_serial.in_waiting < 1:
                pass
            read_data = arduino_serial.read(1)
            self.current_angle = int.from_bytes(read_data, byteorder='little', signed=False)
            send_ack(to_arduino=1)  # send ack to the arduino, to inc/dec the servo motor
            if self.max_dist_scale.get() >= dist >= self.min_dist_scale.get():
                print(f"Found object in dist:{dist}, and angle:{self.current_angle}")
                x_target = CENTER_X + dist * math.cos(math.radians(self.current_angle))/2
                y_target = CENTER_Y - dist * math.sin(math.radians(self.current_angle))/2  # Adjusted for upper side
                # Animate a fading effect of the blip
                for i in range(4):
                    self.radar_canvas.create_oval(x_target - 5, y_target - 5, x_target + 5, y_target + 5, width=2,
                                              fill=f"red{4-i}", tags=f"blip_{self.blip_id}_{i+1}")
                    self.root.after(5000-1000*(i+1), self.radar_canvas.delete, f"blip_{self.blip_id}_{i+1}")
                self.blip_id += 1
            # Update the scan line
            x_line = CENTER_X + LINE_LENGTH * math.cos(math.radians(self.current_angle))
            y_line = CENTER_Y - LINE_LENGTH * math.sin(math.radians(self.current_angle))  # Adjusted for upper side
            self.radar_canvas.delete("line")  # Clear previous line
            self.radar_canvas.create_line(CENTER_X, CENTER_Y, x_line, y_line, fill="green1", width=1, tags="line")
            self.root.update()  # Update the display
            self.root.after(10, self.update_radar_display)  # Recursive call for animation


if __name__ == "__main__":
    esp32_serial = serial.Serial('COM5', BAUD_RATE)  # Change 'COMX' to your ESP32's UART port
    esp32_serial.flushInput()
    esp32_serial.flushOutput()

    arduino_serial = serial.Serial('COM3', BAUD_RATE)  # Change 'COMX' to your Arduino UART port
    arduino_serial.flushInput()
    arduino_serial.flushOutput()
    root = tk.Tk()
    app = RadarControlApp(root)
    root.mainloop()
