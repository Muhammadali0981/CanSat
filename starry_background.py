from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QTimer, QPoint
import random

class Star:
    def __init__(self, x, y, brightness):
        self.x = x
        self.y = y
        self.brightness = brightness
        self.direction = 1  # 1 for increasing brightness, -1 for decreasing

class StarryBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stars = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stars)
        self.timer.start(500)  # Update every 50 ms

    def create_stars(self):
        num_stars = int(self.width() * self.height() / 1000)  # Adjust for desired star density
        self.stars = [
            Star(random.randint(0, self.width()),
                 random.randint(0, self.height()),
                 random.randint(0, 255))
            for _ in range(num_stars)
        ]

    def update_stars(self):
        for star in self.stars:
            star.brightness += star.direction * 5
            if star.brightness <= 0 or star.brightness >= 255:
                star.direction *= -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)

        for star in self.stars:
            painter.setPen(QColor(255, 255, 255, star.brightness))
            painter.drawPoint(QPoint(star.x, star.y))

    def resizeEvent(self, event):
        self.create_stars()
        super().resizeEvent(event)