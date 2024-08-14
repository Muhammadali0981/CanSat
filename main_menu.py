import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QGraphicsOpacityEffect, 
                             QLabel, QStackedWidget, QDialog, QComboBox, QFormLayout, QDialogButtonBox, QLineEdit, QHBoxLayout)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QTimer, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush
from arduino_gui import ArduinoGUI
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QPixmap

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")

        self.setStyleSheet("""
            QPushButton {
                font-size: 36px;
                padding: 20px;
                width: 300px;
                height: 100px;
                background-color: black;
                color: yellow;
                border: 2px solid yellow;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: yellow;
                color: black;
                border: 2px solid black;
            }
        """)

    def start_animation(self, start_pos, end_pos):
        self.setGeometry(start_pos)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QEasingCurve.OutBounce)

        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        self.opacity_animation.setDuration(1000)

        self.animation.start()
        self.opacity_animation.start()

    def animate_out(self, end_pos):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(end_pos)
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QEasingCurve.InBack)

        self.opacity_animation.setStartValue(1)
        self.opacity_animation.setEndValue(0)
        self.opacity_animation.setDuration(1000)

        self.animation.start()
        self.opacity_animation.start()

class OptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options")
        self.setStyleSheet("color: yellow; background-color: black;")

        layout = QFormLayout(self)

        # COM Port selection
        self.com_port_combo = QComboBox()
        self.update_com_ports()
        layout.addRow("COM Port:", self.com_port_combo)

        # Baud Rate
        self.baud_rate_edit = QLineEdit("9600")
        layout.addRow("Baud Rate:", self.baud_rate_edit)

        # Refresh COM ports button
        self.refresh_button = QPushButton("Refresh COM Ports")
        self.refresh_button.setStyleSheet(self.get_button_stylesheet())
        self.refresh_button.clicked.connect(self.update_com_ports)
        layout.addRow(self.refresh_button)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        # Apply custom styles to the buttons in QDialogButtonBox
        for button in button_box.buttons():
            button.setStyleSheet(self.get_button_stylesheet())

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

    def update_com_ports(self):
        self.com_port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_port_combo.addItems(ports)
        if ports:
            self.com_port_combo.setCurrentIndex(0)

    def get_settings(self):
        return {
            "com_port": self.com_port_combo.currentText(),
            "baud_rate": int(self.baud_rate_edit.text())
        }

    def get_button_stylesheet(self):
        return """
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
                border: 2px solid black;
            }
        """

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CanSat Space Mission")
        self.setStyleSheet("color: yellow; background-color: black;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.menu_layout.setAlignment(Qt.AlignCenter)
        self.stacked_widget.addWidget(self.menu_widget)

        # Add spacing to push the logo and title down
        self.menu_layout.addSpacing(100)  # Adjust this value to control the vertical position

        # Add logo
        self.logo_label = QLabel()
        logo_pixmap = QPixmap("NCGSA-logo.png")
        scaled_logo = logo_pixmap.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(scaled_logo)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.menu_layout.addWidget(self.logo_label)

        # Add title
        self.title_label = QLabel("CanSat Space Mission")
        self.title_label.setStyleSheet("color: yellow; font-size: 48px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.menu_layout.addWidget(self.title_label)

        # Add spacing to push title and logo higher
        self.menu_layout.addSpacing(50)

        self.start_button = AnimatedButton("Start")
        self.start_button.clicked.connect(self.start_application)
        self.menu_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        self.options_button = AnimatedButton("Options")
        self.options_button.clicked.connect(self.show_options)
        self.menu_layout.addWidget(self.options_button, alignment=Qt.AlignCenter)

        self.exit_button = AnimatedButton("Exit")
        self.exit_button.clicked.connect(self.exit_application)
        self.menu_layout.addWidget(self.exit_button, alignment=Qt.AlignCenter)

        # Add a stretchable space to push the credits to the bottom
        self.menu_layout.addStretch()

        # Create a container for credits and set its layout
        credits_container = QWidget()
        credits_layout = QHBoxLayout(credits_container)
        credits_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        # Add credits label to the layout
        self.credits_label = QLabel("Created by Shaheer Muhammad Shahbaz and Muhammad Ali")
        self.credits_label.setStyleSheet("color: yellow; font-size: 14px;")
        credits_layout.addWidget(self.credits_label)
        
        # Add credits container to the main layout
        self.main_layout.addWidget(credits_container, alignment=Qt.AlignBottom | Qt.AlignRight)

        # Make the window full-screen
        self.showFullScreen()    

        # Default settings
        self.arduino_settings = self.get_default_settings()

        # Initialize Arduino GUI with settings
        self.arduino_gui = ArduinoGUI(self, self.arduino_settings)
        self.stacked_widget.addWidget(self.arduino_gui)

        # Start the buttons from the bottom of the screen
        self.start_button.setGeometry(QRect(self.width() // 2 - 150, self.height(), 300, 100))
        self.options_button.setGeometry(QRect(self.width() // 2 - 150, self.height(), 300, 100))
        self.exit_button.setGeometry(QRect(self.width() // 2 - 150, self.height(), 300, 100))
        
        self.start_button.start_animation(QRect(self.width() // 2 - 150, self.height(), 300, 100), QRect(self.width() // 2 - 150, self.height() // 2 - 75, 300, 100))
        self.options_button.start_animation(QRect(self.width() // 2 - 150, self.height(), 300, 100), QRect(self.width() // 2 - 150, self.height() // 2 + 75, 300, 100))
        self.exit_button.start_animation(QRect(self.width() // 2 - 150, self.height(), 300, 100), QRect(self.width() // 2 - 150, self.height() // 2 + 225, 300, 100))
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        palette = self.central_widget.palette()
        self.central_widget.setPalette(palette)

    def start_application(self):
        self.start_button.animate_out(QRect(self.width() // 2 - 150, -100, 300, 100))
        self.options_button.animate_out(QRect(self.width() // 2 - 150, -100, 300, 100))
        self.exit_button.animate_out(QRect(self.width() // 2 - 150, -100, 300, 100))
        QTimer.singleShot(1000, self.show_arduino_gui)

    def get_default_settings(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return {
            "com_port": ports[0] if ports else "COM1",
            "baud_rate": 9600
        }

    def exit_application(self):
        self.exit_button.animate_out(QRect(self.width() // 2 - 150, self.height() + 100, 300, 100))
        self.options_button.animate_out(QRect(self.width() // 2 - 150, self.height() + 100, 300, 100))
        self.start_button.animate_out(QRect(self.width() // 2 - 150, self.height() + 100, 300, 100))
        QTimer.singleShot(1000, QApplication.quit)

    def show_arduino_gui(self):
        self.stacked_widget.setCurrentWidget(self.arduino_gui)
        self.arduino_gui.fade_in()

    def show_options(self):
        options_dialog = OptionsDialog(self)
        options_dialog.com_port_combo.setCurrentText(self.arduino_settings["com_port"])
        options_dialog.baud_rate_edit.setText(str(self.arduino_settings["baud_rate"]))
        if options_dialog.exec_() == QDialog.Accepted:
            self.arduino_settings = options_dialog.get_settings()
            self.arduino_gui.update_settings(self.arduino_settings)

    def show_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.menu_widget)
        self.start_button.start_animation(QRect(self.width() // 2 - 150, -100, 300, 100), QRect(self.width() // 2 - 150, self.height() // 2 - 75, 300, 100))
        self.options_button.start_animation(QRect(self.width() // 2 - 150, -100, 300, 100), QRect(self.width() // 2 - 150, self.height() // 2 + 75, 300, 100))
        self.exit_button.start_animation(QRect(self.width() // 2 - 150, -100, 300, 100), QRect(self.width() // 2 - 150, self.height() // 2 + 225, 300, 100))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())