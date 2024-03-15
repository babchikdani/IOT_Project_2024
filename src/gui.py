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
ROOM_SCAN_DONE_SIGNAL = 'Room Scan Done!\n'
STOP_CMD = 0
START_CMD = 1
ROOM_SCAN_CMD = 2
DISTANCE_BYTES = 4
ANGLE_BYTES = 4

esp32_serial = serial.Serial('COM5', BAUD_RATE)  # Change 'COMX' to your ESP32's UART port
esp32_serial.flushInput()
esp32_serial.flushOutput()

arduino_serial = serial.Serial('COM3', BAUD_RATE)  # Change 'COMX' to your ESP32's UART port
arduino_serial.flushInput()
arduino_serial.flushOutput()


def send_metrics(speed=1, max_angle=180, min_angle=0, max_dist=700, min_dist=50, cmd=1, send_to_esp32=0, send_to_arduino=0):
    # Send the data to the ESP32
    speed_byte = speed.to_bytes(1, 'big')
    min_angle_byte = min_angle.to_bytes(1, 'big')
    max_angle_byte = max_angle.to_bytes(1,'big')
    # min dist value may be bigger than 255, split it into bytes
    min_dist_msb = (min_dist >> 8) & 0xFF  # Shift right by 8 bits to get the MSB
    min_dist_lsb = min_dist & 0xFF  # Mask to get the LSB
    min_dist_msb_byte = min_dist_msb.to_bytes(1, 'big')
    min_dist_lsb_byte = min_dist_lsb.to_bytes(1, 'big')
    # Do the same for max_dist
    max_dist_msb = (max_dist >> 8) & 0xFF  # Shift right by 8 bits to get the MSB
    max_dist_lsb = max_dist & 0xFF  # Mask to get the LSB
    max_dist_msb_byte = max_dist_msb.to_bytes(1, 'big')
    max_dist_lsb_byte = max_dist_lsb.to_bytes(1, 'big')
    cmd_byte = cmd.to_bytes(1, 'big')
    if send_to_esp32:
        bytes_list_esp32 = [cmd_byte]
        data_to_send_esp32 = b''.join(bytes_list_esp32)
        esp32_serial.flushOutput()
        esp32_serial.write(data_to_send_esp32)
        print("Data was sent successfully to esp32")
    if send_to_arduino:
        bytes_list_arduino = [speed_byte, max_angle_byte, min_angle_byte, max_dist_msb_byte, max_dist_lsb_byte, min_dist_msb_byte,
                      min_dist_lsb_byte, cmd_byte]
        data_to_send_arduino = b''.join(bytes_list_arduino)
        arduino_serial.flushOutput()
        arduino_serial.write(data_to_send_arduino)
        print("Data was sent successfully to arduino")
    print('Data sent successfully.')


class RadarControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kiponet Barzel Control")
        self.blip_id = 0

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
        self.scan_room_button = tk.Button(root, text="Room Scan", command=self.room_scan, bg="blue", width=20, height=2,
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

        self.scan_room_button.grid(row=5, column=0, columnspan=1, padx=pad_x, pady=pad_y)

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

    def read_lidar(self):
        while esp32_serial.in_waiting < 1:
            continue
        incoming_data = esp32_serial.readline().decode()
        print("incoming_data:" + str(incoming_data[:-1]))
        dist = int(incoming_data[:-1])
        print("dist:" + str(dist))
        return dist

    def read_servo(self):
        while arduino_serial.in_waiting < 1:
            pass
        incoming_data = arduino_serial.readline().decode()
        print("incoming_data:" + str(incoming_data[:-1]))
        angle = int(incoming_data[:-1])
        print("angle:" + str(angle))
        return angle

    def check_scales_input(self):
        if self.min_angle_scale.get() > self.max_angle_scale.get():
            tk.messagebox.showwarning("Warning", "Minimum Angle cannot be larger than Maximum Angle")
            return 1
        if self.min_dist_scale.get() > self.max_dist_scale.get():
            tk.messagebox.showwarning("Warning", "Minimum Scan Distance cannot be larger than Maximum Scan "
                                                 "Distance")
            return 1    # 1 is error
        return 0 # 0 is success

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

    def send_ack(self, to_esp=0, to_arduino=0):
        ack = 1
        ack_byte = ack.to_bytes(1, 'big')
        bytes_list = [ack_byte]
        data_to_send = b''.join(bytes_list)
        if to_esp:
            esp32_serial.write(data_to_send)
        if to_arduino:
            arduino_serial.write(data_to_send)

    # Sends a room_scan (cmd=2) to the ESP and reads the response. Updates the Radar Canvas temporarily.
    def room_scan(self):
        print("Initial room scanning started.")
        self.radar_canvas.delete("standby")
        self.radar_canvas.create_text(70, 20, text="Initial Room Scan", fill="wheat", font=("Arial", 10, "bold"),
                                      tags="initial_scanning")
        self.radar_canvas.update()
        self.disable_scales()
        send_metrics(cmd=ROOM_SCAN_CMD, send_to_esp32=1, send_to_arduino=1)  # maybe move the send_metrics() to self.send_metrics()
        # Check if there's any response from the device
        if esp32_serial.in_waiting > 0:
            # Read the response. The respone MUST END WITH '\n'!
            time.sleep(0.3)
            response = esp32_serial.readline().decode()
            print("Received:", response)
        while arduino_serial.in_waiting < 8:
            pass
        if arduino_serial.in_waiting > 0:
            # Read the response. The response MUST END WITH '\n'!
            response = arduino_serial.readline().decode()
            print("skrt:", response)
        print("System ready.")
        self.scanning = True    #TODO: remove this?
        self.update_radar_display()
        self.enable_scales()
        self.radar_canvas.delete("initial_scanning")
        self.radar_canvas.create_text(40, 20, text="Standby", fill="green", font=("Arial", 10, "bold"), tags="standby")

    def start_scan(self):
        # esp32_serial.flushInput()
        if self.check_scales_input() == 1:
            return
        if not self.scanning:
            # Start radar scanning logic here
            print("Radar scanning started.")
            send_metrics(speed=self.speed_scale.get(), max_angle=self.max_angle_scale.get(),
                         min_angle=self.min_angle_scale.get(), max_dist=self.max_dist_scale.get(),
                         min_dist=self.min_dist_scale.get(), cmd=START_CMD)
            self.disable_scales()
            self.scanning = True
            self.update_radar_display()
            # self.current_angle += 1
            self.radar_canvas.delete("standby")
            self.radar_canvas.create_text(40, 20, text="Scanning", fill="green", font=("Arial", 10, "bold"),
                                          tags="scanning")

    def stop_scan(self):
        if self.scanning:
            # Stop radar scanning logic here
            send_metrics(cmd=STOP_CMD)
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
            dist = self.read_lidar()
            self.current_angle = self.read_servo()
            self.send_ack(to_arduino=1)  # send ack to the arduino, to inc/dec the servo motor
            if dist >= 0:
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
            x = CENTER_X + LINE_LENGTH * math.cos(math.radians(self.current_angle))
            y = CENTER_Y - LINE_LENGTH * math.sin(math.radians(self.current_angle))  # Adjusted for upper side
            self.radar_canvas.delete("line")  # Clear previous line
            self.radar_canvas.create_line(CENTER_X, CENTER_Y, x, y, fill="green1", width=1, tags="line")
            self.root.update()  # Update the display
            self.root.after(1, self.update_radar_display)  # Recursive call for animation


if __name__ == "__main__":
    root = tk.Tk()
    app = RadarControlApp(root)
    root.mainloop()