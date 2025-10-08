import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QScrollArea, QGroupBox, QWidget)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
from models.service import get_all_services


class ServicesPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Available Services")
        self.setWindowIcon(QIcon("src/gui/a_logo.png"))
        self.setFixedSize(1000, 600)
        self.setStyleSheet("background-color: #f9f9f9;")

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # === Header with Back Button and Logo ===
        header = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setFixedSize(80, 30)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e6e6fa;
                border: 1px solid #122620;
                border-radius: 15px;
                font-size: 12px;
                font-style: italic;
                padding: 5px;
            }
            QPushButton:hover { background-color: #a3b68b; }
        """)
        back_btn.clicked.connect(self.reject)

        logo = QLabel()
        pixmap = QPixmap("src/gui/a_main_logo.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaledToHeight(
                50, Qt.TransformationMode.SmoothTransformation))
        logo.setFixedHeight(50)

        header.addWidget(back_btn)
        header.addStretch()
        header.addWidget(logo)
        main_layout.addLayout(header)

        # === Scrollable Services List ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout(container)

        services = get_all_services()
        if not services:
            no_service = QLabel("No services available.")
            no_service.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container_layout.addWidget(no_service)
        else:
            grouped = {}
            for s in services:
                grouped.setdefault(s["category_name"], []).append(s)

            ordered_categories = ["Standard",
                                  "Specialized", "Dry Cleaning", "Add Ons"]
            for category in ordered_categories:
                if category not in grouped:
                    continue

                cat_box = QGroupBox(category)
                cat_box.setStyleSheet("""
                    QGroupBox {
                        background-color: #e6e6fa;
                        border: 2px solid #d8cbef;
                        border-radius: 10px;
                        font-size: 14px;
                        margin-top: 10px;
                        padding: 10px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 5px 10px;
                        background-color: #d8cbef;
                        border-radius: 5px;
                    }
                """)
                cat_layout = QVBoxLayout()

                for s in grouped[category]:
                    row = QHBoxLayout()
                    name_label = QLabel(f"• {s['service_name']}")
                    name_label.setStyleSheet(
                        "background-color: transparent ; font-size: 13px; font-weight: italic;")

                    price_label = QLabel(
                        f"₱{float(s['min_price']):,.2f} - ₱{float(s['max_price']):,.2f} ({s['price_unit']})"
                    )
                    price_label.setStyleSheet(
                        "color: gray; font-size: 12px; margin-left: 10px;")

                    row.addWidget(name_label)
                    row.addStretch()
                    row.addWidget(price_label)

                    container_row = QWidget()
                    container_row.setLayout(row)
                    container_row.setStyleSheet(
                        "background-color: transparent;")
                    cat_layout.addWidget(container_row)

                cat_box.setLayout(cat_layout)
                container_layout.addWidget(cat_box)

        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

        # Footer
        footer = QLabel(
            "💬 For inquiries: 0912-345-6789 | la_lavandera@gmail.com")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("""
            QLabel {
                background-color: #e6e6fa;
                border-top: 1px solid #ccc;
                padding: 6px;
                font-size: 11px;
                color: #333;
                font-style: italic;
                border-radius: 15px;
            }
        """)
        main_layout.addWidget(footer)
