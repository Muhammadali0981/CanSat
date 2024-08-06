import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import serial
import json
from datetime import datetime, timedelta

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CanSat Data")

        # Create labels for displaying data
        self.yaw_label = QLabel("Yaw: N/A")
        self.pitch_label = QLabel("Pitch: N/A")
        self.roll_label = QLabel("Roll: N/A")
        self.temp_label = QLabel("Temperature: N/A")
        self.pressure_label = QLabel("Pressure: N/A")
        self.altitude_label = QLabel("Altitude: N/A")
        self.location_label = QLabel("Location: Signal not available")
        self.date_time_gmt_label = QLabel("Date/Time (GMT): Signal not available")
        self.date_time_pkt_label = QLabel("Date/Time (PKT): Signal not available")

        layout = QVBoxLayout()
        layout.addWidget(self.yaw_label)
        layout.addWidget(self.pitch_label)
        layout.addWidget(self.roll_label)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.pressure_label)
        layout.addWidget(self.altitude_label)
        layout.addWidget(self.location_label)
        layout.addWidget(self.date_time_gmt_label)
        layout.addWidget(self.date_time_pkt_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        try:
            # Replace 'COM3' with the COM port used by your USB-to-TTL converter
            self.serial_port = serial.Serial('COM3', 9600)
        except serial.SerialException as e:
            print(f"Serial port error: {e}")
            sys.exit(1)

        self.buffer = ""
        self.previous_values = {
            "yaw": "N/A",
            "pitch": "N/A",
            "roll": "N/A",
            "temperature": "N/A",
            "pressure": "N/A",
            "altitude": "N/A",
            "location": "Signal not available",
            "date_time_gmt": "Signal not available",
            "date_time_pkt": "Signal not available"
        }
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial_data)
        self.timer.start(100)  # Check for new data every 100ms

    def read_serial_data(self):
        try:
            # Read data from serial port
            if self.serial_port.in_waiting > 0:
                self.buffer += self.serial_port.read(self.serial_port.in_waiting).decode('utf-8')
                lines = self.buffer.split('\n')

                # Process each line of data
                for line in lines:
                    if line.strip():
                        print(f"Raw data received: {line.strip()}")  # Print raw data for debugging
                        self.parse_data(line.strip())
                
                # Clear buffer after processing
                self.buffer = ""
        except Exception as e:
            print(f"Error reading serial data: {e}")

    def parse_data(self, data):
        try:
            print(f"Parsing data: {data}")  # Print data being parsed for debugging
            json_data = json.loads(data)

            # Update GUI with parsed data
            if "yaw" in json_data:
                self.previous_values["yaw"] = json_data["yaw"]
                self.yaw_label.setText(f"Yaw: {self.previous_values['yaw']}")

            if "pitch" in json_data:
                self.previous_values["pitch"] = json_data["pitch"]
                self.pitch_label.setText(f"Pitch: {self.previous_values['pitch']}")

            if "roll" in json_data:
                self.previous_values["roll"] = json_data["roll"]
                self.roll_label.setText(f"Roll: {self.previous_values['roll']}")

            if "temperature" in json_data:
                self.previous_values["temperature"] = json_data["temperature"]
                self.temp_label.setText(f"Temperature: {self.previous_values['temperature']}")

            if "pressure" in json_data:
                self.previous_values["pressure"] = json_data["pressure"]
                self.pressure_label.setText(f"Pressure: {self.previous_values['pressure']}")

            if "altitude" in json_data:
                self.previous_values["altitude"] = json_data["altitude"]
                self.altitude_label.setText(f"Altitude: {self.previous_values['altitude']}")

            if "location" in json_data:
                self.previous_values["location"] = json_data["location"]
                self.location_label.setText(f"Location: {self.previous_values['location']}")

            if "date" in json_data and "time" in json_data:
                self.previous_values["date_time_gmt"] = f"{json_data['date']} {json_data['time']}"
                gmt_time = datetime.strptime(self.previous_values["date_time_gmt"], "%m/%d/%Y %H:%M:%S.%f")
                pkt_time = gmt_time + timedelta(hours=5)
                self.previous_values["date_time_pkt"] = pkt_time.strftime("%m/%d/%Y %H:%M:%S.%f")

                self.date_time_gmt_label.setText(f"Date/Time (GMT): {self.previous_values['date_time_gmt']}")
                self.date_time_pkt_label.setText(f"Date/Time (PKT): {self.previous_values['date_time_pkt']}")

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except Exception as e:
            print(f"Error parsing data: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
