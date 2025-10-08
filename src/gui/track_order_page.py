import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QApplication, QScrollArea, QWidget
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

# --- Import models ---
from models.order import get_order_by_id
from models.customer import get_customer_by_id
from models.order_status import get_order_status_by_id
from models.order_item import get_order_items_by_order
from models.payment import get_payments_by_order
from models.payment_method import get_payment_method_by_id
from models.payment_status import get_payment_status_by_id
from models.service import get_service_by_id


class TrackOrderDialog(QDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        self.setWindowTitle(f"Order #{order_id} - Details & Receipt")
        self.setWindowIcon(QIcon("src/gui/a_logo.png"))
        self.setFixedSize(1000, 650)
        self.setStyleSheet("background-color: #f9f9f9;")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # === LOGO ===
        logo_label = QLabel()
        pixmap = QPixmap("src/gui/a_main_logo.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaledToHeight(
                60, Qt.TransformationMode.SmoothTransformation))
        logo_label.setFixedHeight(60)
        layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # === TITLE ===
        title = QLabel(f"Order Tracking ID: {self.order_id}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 20px; font-style: italic; color: #4b0082;")
        layout.addWidget(title)

        # === FETCH ALL INFO ===
        try:
            order = get_order_by_id(self.order_id)
            if not order:
                QMessageBox.warning(self, "Not Found", "Order not found.")
                self.reject()
                return

            customer = get_customer_by_id(order["customer_id"])
            status = get_order_status_by_id(order["order_status_id"])
            payments = get_payments_by_order(self.order_id)
            payment = payments[0] if payments else None
            items = get_order_items_by_order(self.order_id)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load order details:\n{e}")
            self.reject()
            return

        # === ORDER STATUS ===
        status_label = QLabel(
            f"Order Status: {status.get('order_status_name', '-') if status else '-'}")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet(
            "font-size: 20px; color: #4b0082; font-weight: 600;")
        layout.addWidget(status_label)

        def make_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(
                "font-size: 13px; color: #122620; background-color: transparent; font-style: italic;")
            return lbl

        # === CUSTOMER INFO BOX ===
        customer_box = QGroupBox("Customer Information")
        customer_box.setStyleSheet("""
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
                font-weight: bold;
                color: #122620;
            }
            QLabel {
                background-color: transparent;
                font-size: 13px;
                color: #122620;
                font-style: italic;
            }
        """)
        cust_layout = QVBoxLayout()
        cust_layout.setSpacing(8)
        cust_layout.addWidget(make_label(
            f"Customer Name: {customer.get('customer_name', '-') if customer else '-'}"))
        cust_layout.addWidget(make_label(
            f"Contact Number: {customer.get('contact_number', '-') if customer else '-'}"))
        order_date = order.get("order_date")
        if isinstance(order_date, datetime):
            order_date = order_date.strftime("%Y-%m-%d %H:%M:%S")
        cust_layout.addWidget(make_label(f"Order Date: {order_date}"))
        customer_box.setLayout(cust_layout)

        # === PAYMENT INFO BOX ===
        payment_box = QGroupBox("Payment Information")
        payment_box.setStyleSheet(customer_box.styleSheet())
        pay_layout = QVBoxLayout()
        pay_layout.setSpacing(8)

        if payment:
            amount_paid = float(payment.get("amount_paid", 0))
            pay_date = payment.get("payment_date")
            if isinstance(pay_date, datetime):
                pay_date = pay_date.strftime("%Y-%m-%d %H:%M:%S")

            # fetch names manually if missing
            payment_method_name = payment.get("payment_method_name")
            if not payment_method_name and payment.get("payment_method_id"):
                method = get_payment_method_by_id(payment["payment_method_id"])
                payment_method_name = method.get(
                    "payment_method_name", "-") if method else "-"

            payment_status_name = payment.get("payment_status_name")
            if not payment_status_name and payment.get("payment_status_id"):
                status_data = get_payment_status_by_id(
                    payment["payment_status_id"])
                payment_status_name = status_data.get(
                    "payment_status_name", "-") if status_data else "-"

            pay_layout.addWidget(make_label(
                f"Amount Paid: ₱{amount_paid:.2f}"))
            pay_layout.addWidget(make_label(f"Payment Date: {pay_date}"))
            pay_layout.addWidget(make_label(f"Method: {payment_method_name}"))
            pay_layout.addWidget(make_label(f"Status: {payment_status_name}"))
        else:
            pay_layout.addWidget(QLabel("No payment record found."))

        payment_box.setLayout(pay_layout)

        # === CUSTOMER + PAYMENT SIDE BY SIDE ===
        info_row = QHBoxLayout()
        info_row.addWidget(customer_box, stretch=1)
        info_row.addWidget(payment_box, stretch=1)
        layout.addLayout(info_row)

        # === ORDER ITEMS ===
        items_box = QGroupBox("Order Items")
        items_box.setStyleSheet(customer_box.styleSheet())
        items_layout = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            ["Service Name", "Quantity", "Price", "Subtotal"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setRowCount(len(items))

        for r, item in enumerate(items):
            service = get_service_by_id(item["service_id"])
            service_name = service["service_name"] if service else "Unknown"

            qty = item["quantity"]
            price = float(item["price"])
            subtotal = qty * price

            table.setItem(r, 0, QTableWidgetItem(service_name))
            table.setItem(r, 1, QTableWidgetItem(str(qty)))
            table.setItem(r, 2, QTableWidgetItem(f"₱{price:.2f}"))
            table.setItem(r, 3, QTableWidgetItem(f"₱{subtotal:.2f}"))

        items_layout.addWidget(table)
        items_box.setLayout(items_layout)
        layout.addWidget(items_box)

        # === CLOSE BUTTON ===
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(120)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #c8b3ee;
                border-radius: 10px;
                font-size: 14px;
                padding: 8px 15px;
            }
            QPushButton:hover { background-color: #b39ddb; }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)


# --- Standalone Test ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = TrackOrderDialog(1)
    dlg.exec()
