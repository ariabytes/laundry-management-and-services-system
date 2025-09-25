import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("La Lavandera")
        self.setWindowIcon(QIcon("src/gui/a_logo.png"))

        self.setStyleSheet("background-color: #f9f9f9;")
        self.initUI()

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

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        vbox = QVBoxLayout(central_widget)

        # --- Top bar with Admin button ---
        topbar = QHBoxLayout()
        topbar.addStretch()  # pushes button to the right
        admin_btn = QPushButton("Admin Log In")
        admin_btn.setFixedSize(85, 30)  # make it small
        admin_btn.setStyleSheet("""
            QPushButton {
                background-color: #e6e6fa;
                border: 1px solid #122620;
                border-radius: 5px;
                font-size: 12px;
                font-style: italic;
                padding: 5px; }
            QPushButton:hover {
                background-color: #a3b68b; }
            QPushButton:pressed {
                background-color: #99af70; }                                                                
            """)
        topbar.addWidget(admin_btn)
        vbox.addLayout(topbar)

        # Icon Label
        self.icon_label = QLabel()
        self.icon_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(self.icon_label)

        # Load original pixmap once
        self.original_pixmap = QPixmap("src/gui/a_main_logo.png")
        self.update_icon()

        # INFO CENTER?

        # Button row (HBox)
        hbox = QHBoxLayout()
        btn1 = QPushButton("Services")
        btn2 = QPushButton("Contact Us")
        btn3 = QPushButton("More Info")

        # Apply style to each button
        self.buttons_style(btn1)
        self.buttons_style(btn2)
        self.buttons_style(btn3)

        hbox.addWidget(btn1)
        hbox.addWidget(btn2)
        hbox.addWidget(btn3)

        # Add the HBox into the VBox
        vbox.addLayout(hbox)

# FOR BUTTONS

    def buttons_style(self, button):
        button.setStyleSheet("""
            QPushButton {
                background-color: #e6e6fa;
                border: 1px solid #122620;
                border-radius: 5px;
                font-size: 16px;
                font-style: italic;
                padding: 10px; }
            QPushButton:hover {
                background-color: #c8b3ee; }
            QPushButton:pressed {
                background-color: #b9a9f6; }                                                                
            """)

# FOR ICON

    def resizeEvent(self, event):
        """Called whenever the window is resized"""
        self.update_icon()
        super().resizeEvent(event)

    def update_icon(self):
        if not self.original_pixmap.isNull():
            # Scale full width, fixed height (like a banner)
            banner_height = 100
            scaled = self.original_pixmap.scaled(
                self.width(), banner_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.icon_label.setPixmap(scaled)
            self.icon_label.setFixedHeight(banner_height)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
