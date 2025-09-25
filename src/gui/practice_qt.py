import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Practice GUI")
        self.setWindowIcon(QIcon("src\gui\practice_icon_qt.jpg"))

        # Desired width and height
        width, height = 1000, 650
        self.resize(width, height)

        # Get screen geometry (primary screen)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Calculate x,y for centering
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2

        # Move the window to center
        self.move(x, y)

        label = QLabel("Hi, QT !", self)
        label.setFont(QFont("Arial", 40))
        label.setGeometry(0, 0, 400, 100)
        label.setStyleSheet("color: blue;"
                            "background-color: #ADD8E6;"
                            "font-weight: bold;"
                            "font-style: italic;"
                            "border-radius: 10px;"
                            "border: 1px white;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter |
                           Qt.AlignmentFlag.AlignBottom)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
