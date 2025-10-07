from gui.admin_page import AdminWindow
from gui.login_page import LoginDialog
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, QWidgetAction, QStyleOptionToolButton, QToolButton, QSizePolicy, QDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QResizeEvent, QAction, QActionEvent
import sys
from pathlib import Path
SRC_DIR = Path(__file__).resolve().parents[1]  # ...\LaundrySystem\src
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("La Lavandera")
        self.admin_win = None  # Will hold the admin page instance
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

        # ---- MAIN OUTER LAYOUT ----
        outer_vbox = QVBoxLayout(central_widget)

        # ---------- HEADER ZONE ----------
        header_vbox = QVBoxLayout()

        # Topbar with Admin button
        topbar = QHBoxLayout()
        topbar.addStretch()
        admin_btn = QPushButton("Admin Log In")
        admin_btn.setFixedSize(90, 30)
        admin_btn.setStyleSheet("""
            QPushButton {
                background-color: #e6e6fa;
                border: 1px solid #122620;
                border-radius: 15px;
                font-size: 12px;
                font-style: italic;
                padding: 5px; }
            QPushButton:hover { background-color: #a3b68b; }
            QPushButton:pressed { background-color: #99af70; }
        """)
        admin_btn.clicked.connect(self.open_admin_via_login)
        topbar.addWidget(admin_btn)
        header_vbox.addLayout(topbar)

        # Banner
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_vbox.addWidget(self.icon_label)

        self.original_pixmap = QPixmap("src/gui/a_main_logo.png")
        self.update_icon()

        # Buttons row
        hbox = QHBoxLayout()
        btn1 = QPushButton("Services")
        btn1.setMaximumSize(150, 40)

        self.buttons_style(btn1)

        hbox.addWidget(btn1)
        header_vbox.addLayout(hbox)

        btn1.clicked.connect(self.open_services_page)

        # Add header zone to outer layout
        outer_vbox.addLayout(header_vbox)

        # ---------- MAIN ZONE (Search bar centered) ----------
        main_vbox = QVBoxLayout()
        main_vbox.addStretch(1)

        # Horizontal layout for search bar + button
        search_hbox = QHBoxLayout()
        search_hbox.setSpacing(0)                     # remove gap
        search_hbox.setContentsMargins(0, 0, 0, 0)    # remove margins

        # Input box
        tracking_input = QLineEdit()
        tracking_input.setPlaceholderText("Enter Your Order Tracking ID")
        tracking_input.setFixedHeight(50)
        tracking_input.setFixedWidth(600)
        tracking_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tracking_input.setStyleSheet("""
            QLineEdit {
                background-color: #e6e6fa;   
                border: 2px solid #122620;   
                border-radius: 25px;
                padding-left: 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #a17fc2;
            }
        """)

        # Search button
        search_btn = QPushButton()
        search_btn.setIcon(QIcon.fromTheme("edit-find"))
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_btn.setFixedSize(40, 40)

        search_btn.clicked.connect(
            lambda: self.open_tracking_dialog(tracking_input.text().strip()))

        search_btn.clicked.connect(lambda: tracking_input.clear())

        self.buttons_style(search_btn)

        search_hbox.addWidget(tracking_input)
        search_hbox.addWidget(search_btn)

        # Center horizontally
        main_vbox.addLayout(search_hbox)
        main_vbox.addStretch(2)

        outer_vbox.addLayout(main_vbox)

        # ---------- FOOTER / CONTACT BANNER ----------
        footer = QHBoxLayout()
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        contact_label = QLabel(
            "0912-345-6789   |   Purok 6, Barangay Gabriela, Davao City   |   la_lavandera@gmail.com")
        contact_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-style: italic;
                color: #333;
                background-color: #e6e6fa;
                border-top: 1px solid #ccc;
                padding: 10px 10px;
                border-radius: 8px;
            }
        """)
        footer.addWidget(contact_label)
        outer_vbox.addLayout(footer)

# FOR BUTTONS

    def buttons_style(self, button):
        button.setStyleSheet("""
            QPushButton {
                background-color: #e6e6fa;
                border: 0px solid #122620;
                border-radius: 20px;
                font-size: 16px;
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

    # FOR TRACKING DIALOG
    def open_tracking_dialog(self, order_id_text):
        if not order_id_text.isdigit():
            QMessageBox.warning(self, "Invalid Input",
                                "Please enter a valid Order ID (numbers only).")
            return

        from gui.track_order_page import TrackOrderDialog
        dlg = TrackOrderDialog(int(order_id_text), self)
        dlg.exec()

    # FOR SERVICES PAGE
    def open_services_page(self):
        from gui.services_page import ServicesPage
        dlg = ServicesPage(self)
        dlg.exec()

    # FOR BACK TO MAINS

    def open_admin_via_login(self):
        dlg = LoginDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:  # ✅ explicit check
            self.open_admin()

    def open_admin(self):
        # Always create a fresh admin window
        if self.admin_win is not None:
            # Clean up any existing window
            try:
                self.admin_win.back_requested.disconnect(self.on_admin_back)
            except:
                pass
            self.admin_win.close()
            self.admin_win = None

        # Create new admin window
        self.admin_win = AdminWindow()
        self.admin_win.back_requested.connect(self.on_admin_back)
        self.admin_win.destroyed.connect(
            lambda: setattr(self, "admin_win", None))

        self.hide()
        self.admin_win.show()
        self.admin_win.activateWindow()
        self.admin_win.raise_()

    def on_admin_back(self):
        if self.admin_win is not None:
            try:
                self.admin_win.back_requested.disconnect(self.on_admin_back)
            except Exception:
                pass
            self.admin_win.close()
            self.admin_win = None  # Add this line!
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
