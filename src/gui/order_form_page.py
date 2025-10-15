import sys
from datetime import datetime
from decimal import Decimal
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGroupBox, QTextEdit, QWidget,
    QScrollArea, QCheckBox, QSpinBox, QComboBox, QDoubleSpinBox,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

# --- Import your models ---
from models.service import get_all_services
from models.payment_method import get_all_payment_methods
from models.payment_status import get_all_payment_statuses
from models.customer_class import add_customer
from models.order import add_order
from models.order_item import add_order_item
from models.payment import add_payment

# NEW: Import OOP classes
from models.order_validator import OrderValidator, PaymentProcessor
from models.status_factory import PaymentStatusFactory


class AddOrderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Order - Form")
        self.setModal(True)
        self.setFixedSize(1300, 700)
        self.setWindowIcon(QIcon("src/gui/a_logo.png"))

        self.service_widgets = []

        # NEW: Create validator instance
        self.validator = OrderValidator()

        self.setStyleSheet("""
            background-color: #f9f9f9;
            QLabel { font-size: 16px; }
            QPushButton { font-size: 14px; }
            QLineEdit, QTextEdit {
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 5px;
            }
        """)

        # === Main Layout ===
        main_layout = QVBoxLayout()

        # === Top Bar ===
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back to Admin Page")
        back_btn.setFixedSize(140, 30)
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
            QPushButton:pressed { background-color: #99af70; }
        """)
        back_btn.clicked.connect(self.reject)

        logo_label = QLabel()
        pixmap = QPixmap("src/gui/a_main_logo.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaledToHeight(
                50, Qt.TransformationMode.SmoothTransformation))
        logo_label.setFixedHeight(50)

        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        top_bar.addWidget(logo_label)
        main_layout.addLayout(top_bar)

        # === Three-column layout ===
        content_layout = QHBoxLayout()
        card_style = """
            QGroupBox {
                background-color: #e6e6fa;
                border: 2px solid #d8cbef;
                border-radius: 15px;
                font-size: 16px;
                font-weight: italic;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 5px 10px;
                background-color: #d8cbef;
                border-radius: 5px;
            }
            QLabel {
                font-size: 13px;
                color: #122620;
            }
        """
        title_style = "background-color: transparent; font-weight: bold; font-size: 11px; color: #666;"

        input_style = """
            QLineEdit, QComboBox, QTextEdit {
                padding: 5px;
                margin-bottom: 5px;
                font-size: 13px;
                border: 1px solid #ccc;
                border-radius: 10px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 2px solid #a17fc2;
            }
        """

        # === Left: Customer Info ===
        customer_box = QGroupBox("Customer Info")
        customer_box.setStyleSheet(card_style)
        customer_box.setFixedWidth(300)
        customer_layout = QVBoxLayout()

        self.customer_name = QLineEdit()
        self.customer_name.setStyleSheet(input_style)
        self.contact_number = QLineEdit()
        self.contact_number.setStyleSheet(input_style)
        self.email = QLineEdit()
        self.email.setStyleSheet(input_style)
        self.address = QTextEdit()
        self.address.setStyleSheet(input_style)

        for label_text, widget in [
            ("Customer Name:", self.customer_name),
            ("Contact Number:", self.contact_number),
            ("Email Address:", self.email)
        ]:
            lbl = QLabel(label_text)
            lbl.setStyleSheet(title_style)
            customer_layout.addWidget(lbl)
            customer_layout.addWidget(widget)

        address_label = QLabel("Address:")
        address_label.setStyleSheet(title_style)
        customer_layout.addWidget(address_label)
        customer_layout.addWidget(self.address)
        customer_box.setLayout(customer_layout)

        # === Middle: Order Items ===
        order_box = QGroupBox("Order Items")
        order_box.setStyleSheet(card_style)
        order_layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ccc;
                border-radius: 10px;
                background-color: white;
            }
        """)
        self.services_container = QWidget()
        self.services_layout = QVBoxLayout()
        self.services_container.setLayout(self.services_layout)
        self.services_container.setStyleSheet(
            """QWidget { background-color: transparent; }""")
        scroll_area.setWidget(self.services_container)
        order_layout.addWidget(scroll_area)
        order_box.setLayout(order_layout)

        # === Right: Payment Info ===
        payment_box = QGroupBox("Payment Info")
        payment_box.setStyleSheet(card_style)
        payment_box.setFixedWidth(300)
        payment_layout = QVBoxLayout()
        payment_layout.setSpacing(8)

        # Total Amount
        total_label = QLabel("Total Amount:")
        total_label.setStyleSheet(title_style)
        self.total_input = QLineEdit()
        self.total_input.setReadOnly(True)
        self.total_input.setStyleSheet(input_style)
        payment_layout.addWidget(total_label)
        payment_layout.addWidget(self.total_input)

        # Amount Paid
        amount_label = QLabel("Amount Paid:")
        amount_label.setStyleSheet(title_style)
        self.amount_paid_input = QLineEdit()
        self.amount_paid_input.setPlaceholderText("Enter amount paid")
        self.amount_paid_input.setStyleSheet(input_style)
        payment_layout.addWidget(amount_label)
        payment_layout.addWidget(self.amount_paid_input)

        # Payment Method
        method_label = QLabel("Payment Method:")
        method_label.setStyleSheet(title_style)
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.setStyleSheet(input_style)
        payment_layout.addWidget(method_label)
        payment_layout.addWidget(self.payment_method_combo)

        # Payment Status
        status_label = QLabel("Payment Status:")
        status_label.setStyleSheet(title_style)
        self.payment_status_combo = QComboBox()
        self.payment_status_combo.setStyleSheet(input_style)
        payment_layout.addWidget(status_label)
        payment_layout.addWidget(self.payment_status_combo)

        payment_layout.addStretch(1)

        payment_box.setLayout(payment_layout)

        # === Footer ===
        footer = QHBoxLayout()
        footer.addStretch()
        save_btn = QPushButton("Add Order")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #c8b3ee;
                border-radius: 15px;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #b39ddb; }
        """)
        save_btn.clicked.connect(self.save_order)
        footer.addWidget(save_btn)

        content_layout.addWidget(customer_box)
        content_layout.addWidget(order_box)
        content_layout.addWidget(payment_box)
        main_layout.addLayout(content_layout)
        main_layout.addLayout(footer)
        self.setLayout(main_layout)

        # Initialize data
        self.load_payment_dropdowns()
        self.load_services()

        # Connect automatic update for Paid status
        self.payment_status_combo.currentTextChanged.connect(
            self.sync_amount_paid)

    # ---------- Load Services ----------
    def load_services(self):
        """Group services by category in fixed order, show price ranges."""
        services = get_all_services()
        if not services:
            return

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
                    background-color: #f1e8ff;
                    border: 1px solid #d8cbef;
                    border-radius: 10px;
                    font-size: 14px;
                    margin-top: 10px;
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
                checkbox = QCheckBox(s["service_name"])
                qty_input = QSpinBox()
                qty_input.setRange(1, 100)
                qty_input.setEnabled(False)

                price_input = QDoubleSpinBox()
                price_input.setRange(
                    float(s["min_price"]), float(s["max_price"]))
                price_input.setValue(
                    float((s["min_price"] + s["max_price"]) / 2))
                price_input.setDecimals(2)
                price_input.setPrefix("₱")
                price_input.setEnabled(False)

                price_hint = QLabel(
                    f"Range: ₱{float(s['min_price']):,.2f} - ₱{float(s['max_price']):,.2f} ({s['price_unit']})"
                )
                price_hint.setStyleSheet(
                    "color: gray; font-size: 11px; margin-left: 5px;")

                checkbox.stateChanged.connect(
                    lambda _, q=qty_input, p=price_input: self.toggle_inputs(q, p))
                checkbox.stateChanged.connect(self.update_total)
                qty_input.valueChanged.connect(self.update_total)
                price_input.valueChanged.connect(self.update_total)

                row.addWidget(checkbox)
                row.addStretch()
                row.addWidget(QLabel("Qty:"))
                row.addWidget(qty_input)
                row.addWidget(QLabel("Price:"))
                row.addWidget(price_input)
                row.addWidget(price_hint)

                container = QWidget()
                container.setLayout(row)
                cat_layout.addWidget(container)

                self.service_widgets.append({
                    "service_id": s.get("service_id"),
                    "service_name": s.get("service_name"),
                    "checkbox": checkbox,
                    "qty": qty_input,
                    "price": price_input
                })

            cat_box.setLayout(cat_layout)
            self.services_layout.addWidget(cat_box)

    def toggle_inputs(self, qty_input, price_input):
        enabled = not qty_input.isEnabled()
        qty_input.setEnabled(enabled)
        price_input.setEnabled(enabled)

    def update_total(self):
        total = 0
        for item in self.service_widgets:
            if item["checkbox"].isChecked():
                total += item["qty"].value() * item["price"].value()
        self.total_input.setText(f"₱{total:,.2f}")
        self.sync_amount_paid()

    def load_payment_dropdowns(self):
        self.payment_method_combo.clear()
        self.payment_status_combo.clear()
        try:
            for m in get_all_payment_methods():
                self.payment_method_combo.addItem(
                    m["payment_method_name"], m["payment_method_id"])
            for s in get_all_payment_statuses():
                self.payment_status_combo.addItem(
                    s["payment_status_name"], s["payment_status_id"])
        except Exception as e:
            print(f"Error loading dropdowns: {e}")

    def sync_amount_paid(self):
        """NEW: Use PaymentStatusFactory to determine amount paid"""
        status_name = self.payment_status_combo.currentText()
        status = PaymentStatusFactory.create(status_name)

        total_text = self.total_input.text().replace("₱", "").replace(",", "").strip()
        try:
            total = Decimal(total_text) if total_text else Decimal("0")
        except:
            total = Decimal("0")

        # Get amount from status object
        amount = status.get_amount_paid(total)

        if not status.can_modify_amount():
            self.amount_paid_input.setText(f"{float(amount):.2f}")
            self.amount_paid_input.setReadOnly(True)
        else:
            self.amount_paid_input.setReadOnly(False)
            if not self.amount_paid_input.text():
                self.amount_paid_input.setText(f"{float(amount):.2f}")

    # ---------- Save Order (UPDATED WITH VALIDATION) ----------
    def save_order(self):
        # Get form data
        name = self.customer_name.text().strip()
        contact = self.contact_number.text().strip()
        email = self.email.text().strip()
        address = self.address.toPlainText().strip()

        # NEW: Use validator class for customer info
        if not self.validator.validate_customer_info(name, contact, email, address):
            QMessageBox.warning(
                self, "Validation Error", self.validator.get_error_message())
            return

        # Collect selected services
        selected = []
        for i in self.service_widgets:
            if i["checkbox"].isChecked():
                selected.append({
                    "service_id": i.get("service_id"),
                    "service_name": i.get("service_name"),
                    "qty": i["qty"].value(),
                    "price": i["price"].value()
                })

        # NEW: Use validator class for order items
        if not self.validator.validate_order_items(selected):
            QMessageBox.warning(
                self, "Validation Error", self.validator.get_error_message())
            return

        # NEW: Use PaymentProcessor to calculate total
        total = PaymentProcessor.calculate_total(selected)

        # NEW: Use validator for payment validation
        amount_paid_text = self.amount_paid_input.text().strip()
        try:
            amount_paid = Decimal(
                amount_paid_text) if amount_paid_text else Decimal("0")
        except:
            amount_paid = Decimal("0")

        payment_status = self.payment_status_combo.currentText()

        if not self.validator.validate_payment(amount_paid, total, payment_status):
            QMessageBox.warning(
                self, "Validation Error", self.validator.get_error_message())
            return

        try:
            # Add customer
            cust_id = add_customer(name, contact, email, address)

            # Get payment info
            method_id = self.payment_method_combo.currentData()
            status_id = self.payment_status_combo.currentData()

            # NEW: Use PaymentStatusFactory to determine payment details
            status = PaymentStatusFactory.create(payment_status)
            payment_date = status.get_payment_date()

            # Determine order status
            from models.order_status import get_all_order_statuses
            all_statuses = get_all_order_statuses()

            if payment_status.lower().strip() == "paid":
                order_status_id = next(
                    (s["order_status_id"] for s in all_statuses if s["order_status_name"].strip(
                    ).lower() == "queueing"),
                    1
                )
            else:
                order_status_id = next(
                    (s["order_status_id"] for s in all_statuses if s["order_status_name"].strip(
                    ).lower() == "pending payment"),
                    1
                )

            # Add order
            order_id = add_order(cust_id, order_status_id,
                                 datetime.now(), total)

            # Add order items
            from models.service import get_all_services
            all_services = get_all_services()
            for sel in selected:
                sid = sel.get("service_id")
                if not sid:
                    svc = next(
                        (s for s in all_services if s["service_name"] == sel["service_name"]), None)
                    sid = svc["service_id"] if svc else None

                if sid is None:
                    print(
                        f"⚠️ Could not determine service_id for {sel.get('service_name')}, skipping item.")
                    continue

                add_order_item(order_id, sid, sel["qty"], float(sel["price"]))

            # Add payment record
            add_payment(order_id, amount_paid,
                        payment_date, method_id, status_id)

            QMessageBox.information(
                self, "Success", "Order successfully added!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save order:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = AddOrderDialog()
    dlg.exec()
