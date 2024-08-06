from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
import pyqtgraph as pg
from starry_background import StarryBackground

class ArduinoGUI(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setStyleSheet("color: yellow;")

        # Create and set the starry background
        self.starry_background = StarryBackground(self)
        self.starry_background.setGeometry(self.rect())

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

        self.data_labels = {}
        for data_type in ['Temperature', 'Humidity', 'Longitude', 'Latitude', 'Yaw', 'Pitch', 'Roll']:
            label = QLabel(f"{data_type}: N/A")
            label.setStyleSheet("font-size: 24px; margin: 10px;")
            data_layout.addWidget(label)
            self.data_labels[data_type] = label

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
        main_content.addWidget(graph_widget)

        self.layout.addLayout(main_content)

        # Set up data (replace this with actual Arduino data in the future)
        self.time_data = []
        self.yaw_data = []
        self.pitch_data = []
        self.roll_data = []

        # Set up fade effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

    def update_data(self, data):
        # This method should be called when new data is received from Arduino
        for key, value in data.items():
            if key in self.data_labels:
                self.data_labels[key].setText(f"{key}: {value}")

        # Update graph data
        self.time_data.append(len(self.time_data))
        self.yaw_data.append(data.get('Yaw', 0))
        self.pitch_data.append(data.get('Pitch', 0))
        self.roll_data.append(data.get('Roll', 0))

        # Update graph
        self.yaw_curve.setData(self.time_data, self.yaw_data)
        self.pitch_curve.setData(self.time_data, self.pitch_data)
        self.roll_curve.setData(self.time_data, self.roll_data)

    def fade_in(self):
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def go_back_to_menu(self):
        self.main_window.show_main_menu()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.starry_background.setGeometry(self.rect())