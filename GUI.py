import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import serial

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CanSat Data")

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Replace 'COM4' with the COM port used by your USB-to-TTL converter
        self.serial_port = serial.Serial('COM3', 9600)

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial_data)
        self.timer.start(10)

    def read_serial_data(self):
        if self.serial_port.in_waiting:
            data = self.serial_port.readline().decode('utf-8').strip()
            self.textEdit.append(data)

app = QApplication([])
window = MainWindow()
window.show()
sys.exit(app.exec_())
