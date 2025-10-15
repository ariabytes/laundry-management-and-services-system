import sys
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

from models import admin


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Login")
        self.setModal(True)
        self.setFixedSize(500, 300)
        self.setWindowIcon(QIcon("src/gui/a_logo.png"))
        self.setStyleSheet("""background-color: #f9f9f9;" 
            QLabel { font-size: 20px; }
            QPushButton { font-size: 15px; }
            QLineEdit { font-size: 14px; }""")

        v = QVBoxLayout(self)

        logo_label = QLabel()
        pixmap = QPixmap("src/gui/a_main_logo.png")

        desired_height = 50
        scaled_pixmap = pixmap.scaledToHeight(
            desired_height,
            Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setFixedHeight(desired_height)

        v.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Enter Admin Credentials")
        label.setStyleSheet(
            "font-size: 20px; font-style: italic; padding: 15px;")
        v.addWidget(label)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")
        self.passw = QLineEdit()
        self.passw.setPlaceholderText("Password")
        self.passw.setEchoMode(QLineEdit.EchoMode.Password)

        self.user.setStyleSheet("""
            QLineEdit { padding: 10px;
            margin-bottom: 10px;    
            font-size: 14px;
            border: 1px solid #ccc;
            border-radius: 5px; }
            QLineEdit:focus { border: 2px solid #a17fc2 }""")
        self.passw.setStyleSheet("""
            QLineEdit { padding: 10px;
            margin-bottom: 10px;    
            font-size: 14px;
            border: 1px solid #ccc;
            border-radius: 5px;}
            QLineEdit:focus { border: 2px solid #a17fc2 }""")

        v.addWidget(self.user)
        v.addWidget(self.passw)

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel")
        ok = QPushButton("Log In")
        ok.setDefault(True)

        self.buttons_style(cancel)
        self.buttons_style(ok)

        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self._try_login)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        v.addLayout(btns)

    def _try_login(self):
        username = self.user.text().strip()
        password = self.passw.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed",
                                "Please enter username and password.")
            return

        record = admin.get_admin_by_username(username)

        if record and record["password"] == password:
            QMessageBox.information(
                self, "Login Success", f"Welcome {record['name']}!")
            self.accept()
        else:
            QMessageBox.critical(self, "Login Failed",
                                 "Invalid username or password.")
            self.user.clear()
            self.passw.clear()

            # self.reject()

    def buttons_style(self, button):
        button.setStyleSheet("""
            QPushButton {
                background-color: #e6e6fa;
                border: 0px solid #122620;
                border-radius: 50px;
                font-size: 13px;
                padding: 10px; }
            QPushButton:hover {
                background-color: #c8b3ee; }
            QPushButton:pressed {
                background-color: #b9a9f6; }                                                                
            """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LoginDialog()
    w.show()
    sys.exit(app.exec())
