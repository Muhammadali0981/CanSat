import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QGraphicsOpacityEffect, QLabel, QStackedWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QTimer, QEasingCurve
from PyQt5.QtGui import QFont, QColor
from starry_background import StarryBackground
from arduino_gui import ArduinoGUI

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        
        self.setStyleSheet(
            "font-size: 36px; padding: 20px; width: 300px; height: 100px;"
            "background-color: black; color: yellow;"
            "border: 2px solid yellow;"
            "border-radius: 10px;"
            "}"
            "QPushButton:hover {"
            "background-color: yellow; color: black;"
            "border: 2px solid black;"
            "}")

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CanSat Space Mission")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Create and set the starry background
        self.starry_background = StarryBackground(self)
        self.starry_background.setGeometry(self.rect())

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.menu_layout.setAlignment(Qt.AlignCenter)
        self.stacked_widget.addWidget(self.menu_widget)

        # Add title
        self.title_label = QLabel("CanSat Space Mission")
        self.title_label.setStyleSheet("color: yellow; font-size: 48px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.menu_layout.addWidget(self.title_label)

        # Add spacing to push title higher
        self.menu_layout.addSpacing(50)

        self.start_button = AnimatedButton("Start Mission")
        self.start_button.clicked.connect(self.start_application)
        self.menu_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        self.exit_button = AnimatedButton("Exit")
        self.exit_button.clicked.connect(self.exit_application)
        self.menu_layout.addWidget(self.exit_button, alignment=Qt.AlignCenter)

        # Make the window full-screen
        self.showFullScreen()

        # Initialize Arduino GUI
        self.arduino_gui = ArduinoGUI(self)
        self.stacked_widget.addWidget(self.arduino_gui)

        # Start the buttons from the bottom of the screen
        self.start_button.setGeometry(QRect(self.width() // 2 - 150, self.height(), 300, 100))
        self.exit_button.setGeometry(QRect(self.width() // 2 - 150, self.height(), 300, 100))
        
        self.start_button.start_animation(QRect(self.width() // 2 - 150, self.height(), 300, 100), QRect(self.width() // 2 - 150, self.height() // 2 + 25, 300, 100))
        self.exit_button.start_animation(QRect(self.width() // 2 - 150, self.height(), 300, 100), QRect(self.width() // 2 - 150, self.height() // 2 + 175, 300, 100))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.starry_background.setGeometry(self.rect())

    def start_application(self):
        self.start_button.animate_out(QRect(self.width() // 2 - 150, -100, 300, 100))
        self.exit_button.animate_out(QRect(self.width() // 2 - 150, -100, 300, 100))
        QTimer.singleShot(1000, self.show_arduino_gui)

    def exit_application(self):
        self.exit_button.animate_out(QRect(self.width() // 2 - 150, self.height() + 100, 300, 100))
        self.start_button.animate_out(QRect(self.width() // 2 - 150, self.height() + 100, 300, 100))
        QTimer.singleShot(1000, QApplication.quit)

    def show_arduino_gui(self):
        self.stacked_widget.setCurrentWidget(self.arduino_gui)
        self.arduino_gui.fade_in()

    def show_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.menu_widget)
        self.start_button.start_animation(QRect(self.width() // 2 - 150, -100, 300, 100), QRect(self.width() // 2 - 150, self.height() // 2 + 25, 300, 100))
        self.exit_button.start_animation(QRect(self.width() // 2 - 150, -100, 300, 100), QRect(self.width() // 2 - 150, self.height() // 2 + 175, 300, 100))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())