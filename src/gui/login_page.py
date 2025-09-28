from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Login")
        self.setModal(True)

        v = QVBoxLayout(self)
        v.addWidget(QLabel("Enter admin credentials"))

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")
        self.passw = QLineEdit()
        self.passw.setPlaceholderText("Password")
        self.passw.setEchoMode(QLineEdit.EchoMode.Password)

        v.addWidget(self.user)
        v.addWidget(self.passw)

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel")
        ok = QPushButton("Log In")
        ok.setDefault(True)
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self._try_login)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        v.addLayout(btns)

    def _try_login(self):
        # TODO: replace with real validation
        if self.user.text().strip() and self.passw.text().strip():
            self.accept()
        else:
            self.reject()
