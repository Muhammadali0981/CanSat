import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect, QApplication
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QColor
import pyqtgraph as pg
import serial
import json
from datetime import datetime, timedelta

class ArduinoGUI(QWidget):
    def __init__(self, main_window, settings):
        super().__init__()
        self.main_window = main_window
        self.settings = settings
        self.setStyleSheet("color: yellow; background-color: black;")

        self.layout = QVBoxLayout(self)

        # Back button
        self.back_button = QPushButton("Back to Main Menu")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: yellow;
                border: 2px solid yellow;
                border-radius: 10px;
                padding: 5px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: yellow;
                color: black;
            }
        """)
        self.back_button.clicked.connect(self.go_back_to_menu)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignLeft | Qt.AlignTop)

        main_content = QHBoxLayout()

        # Data display section
        data_widget = QWidget()
        data_layout = QVBoxLayout(data_widget)
        data_layout.setAlignment(Qt.AlignTop)

        self.data_labels = {
            "yaw": QLabel("Yaw: N/A"),
            "pitch": QLabel("Pitch: N/A"),
            "roll": QLabel("Roll: N/A"),
            "temperature": QLabel("Temperature: N/A"),
            "pressure": QLabel("Pressure: N/A"),
            "altitude": QLabel("Altitude: N/A"),
            "location": QLabel("Location: Signal not available"),
            "date_time_gmt": QLabel("Date/Time (GMT): Signal not available"),
            "date_time_pkt": QLabel("Date/Time (PKT): Signal not available")
        }

        for label in self.data_labels.values():
            label.setStyleSheet("font-size: 24px; margin: 10px;")
            data_layout.addWidget(label)

        main_content.addWidget(data_widget)

        # Graph section
        graph_widget = QWidget()
        graph_layout = QVBoxLayout(graph_widget)
        
        self.graph = pg.PlotWidget()
        self.graph.setBackground('k')
        self.graph.setTitle("Yaw, Pitch, Roll", color='y', size='24pt')
        self.graph.setLabel('left', 'Degrees', color='y', size='20pt')
        self.graph.setLabel('bottom', 'Time', color='y', size='20pt')
        self.graph.showGrid(x=True, y=True)
        self.graph.addLegend()

        self.yaw_curve = self.graph.plot(pen='r', name='Yaw')
        self.pitch_curve = self.graph.plot(pen='g', name='Pitch')
        self.roll_curve = self.graph.plot(pen='b', name='Roll')

        graph_layout.addWidget(self.graph)

        # Refresh button
        self.refresh_button = QPushButton("Refresh Graph")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: yellow;
                color: black;
                border: 2px solid yellow;
                border-radius: 10px;
                padding: 5px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: black;
                color: yellow;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_graph)
        graph_layout.addWidget(self.refresh_button, alignment=Qt.AlignCenter)

        main_content.addWidget(graph_widget)
        self.layout.addLayout(main_content)

        # Set up data
        self.time_data = []
        self.yaw_data = []
        self.pitch_data = []
        self.roll_data = []

        # Set up fade effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        # Set up serial connection
        self.setup_serial_connection()

        self.buffer = ""
        self.previous_values = {key: "N/A" for key in self.data_labels.keys()}
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial_data)
        self.timer.start(100)  # Check for new data every 100ms

    def setup_serial_connection(self):
        try:
            self.serial_port = serial.Serial(self.settings["com_port"], self.settings["baud_rate"])
            print(f"Connected to {self.settings['com_port']} at {self.settings['baud_rate']} baud")
        except serial.SerialException as e:
            print(f"Serial port error: {e}")
            # You might want to show an error message to the user here

    def update_settings(self, new_settings):
        self.settings = new_settings
        if hasattr(self, 'serial_port'):
            self.serial_port.close()
        self.setup_serial_connection()

    def read_serial_data(self):
        try:
            if self.serial_port.in_waiting > 0:
                self.buffer += self.serial_port.read(self.serial_port.in_waiting).decode('utf-8')
                lines = self.buffer.split('\n')
                for line in lines:
                    if line.strip():
                        print(f"Raw data received: {line.strip()}")  # Print raw data for debugging
                        self.parse_data(line.strip())
                self.buffer = ""
        except Exception as e:
            print(f"Error reading serial data: {e}")

    def parse_data(self, data):
        try:
            print(f"Parsing data: {data}")  # Print data being parsed for debugging
            json_data = json.loads(data)

            for key in ["yaw", "pitch", "roll", "temperature", "pressure", "altitude", "location"]:
                if key in json_data:
                    self.previous_values[key] = json_data[key]
                    self.data_labels[key].setText(f"{key.capitalize()}: {self.previous_values[key]}")

            if "date" in json_data and "time" in json_data:
                gmt_time = datetime.strptime(f"{json_data['date']} {json_data['time']}", "%m/%d/%Y %H:%M:%S.%f")
                pkt_time = gmt_time + timedelta(hours=5)
                self.previous_values["date_time_gmt"] = gmt_time.strftime("%m/%d/%Y %H:%M:%S.%f")
                self.previous_values["date_time_pkt"] = pkt_time.strftime("%m/%d/%Y %H:%M:%S.%f")

                self.data_labels["date_time_gmt"].setText(f"Date/Time (GMT): {self.previous_values['date_time_gmt']}")
                self.data_labels["date_time_pkt"].setText(f"Date/Time (PKT): {self.previous_values['date_time_pkt']}")

            # Update graph
            self.time_data.append(len(self.time_data))
            self.yaw_data.append(float(self.previous_values["yaw"]))
            self.pitch_data.append(float(self.previous_values["pitch"]))
            self.roll_data.append(float(self.previous_values["roll"]))

            self.yaw_curve.setData(self.time_data, self.yaw_data)
            self.pitch_curve.setData(self.time_data, self.pitch_data)
            self.roll_curve.setData(self.time_data, self.roll_data)

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except Exception as e:
            print(f"Error parsing data: {e}")

    def refresh_graph(self):
        # Clear the existing data and reset the graph
        self.time_data.clear()
        self.yaw_data.clear()
        self.pitch_data.clear()
        self.roll_data.clear()
        self.yaw_curve.clear()
        self.pitch_curve.clear()
        self.roll_curve.clear()
        print("Graph refreshed")

    def fade_in(self):
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def go_back_to_menu(self):
        self.main_window.show_main_menu()

# For testing purposes
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ArduinoGUI(None, {"com_port": "COM1", "baud_rate": 9600})
    window.show()
    sys.exit(app.exec_())
