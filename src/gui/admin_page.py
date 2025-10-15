import sys

from datetime import datetime
from decimal import Decimal
from models.order import get_all_orders, delete_order, update_order, add_order
from models.customer import get_customer_by_id, get_all_customers, update_customer, add_customer
from models.order_status import get_order_status_by_id, get_all_order_statuses, update_order_status
from models.order_item import get_order_items_by_order, update_order_item, delete_order_item, add_order_item
from models.payment import get_payments_by_order, update_payment, add_payment
from models.service import get_service_by_id, get_all_services
from models.payment_method import get_all_payment_methods
from models.payment_status import get_all_payment_statuses
from models.category import get_all_categories
from gui.order_form_page import AddOrderDialog

from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QAbstractTableModel, QModelIndex
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QTableView, QMessageBox, QInputDialog, QHeaderView, QScrollArea, QFrame, QLineEdit,
                             QComboBox, QTextEdit, QDateEdit, QDoubleSpinBox, QSpinBox, QGroupBox, QFormLayout, QGridLayout, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem, QCheckBox, QStyledItemDelegate)

# -------- TABLE --------


class OrdersTableModel(QAbstractTableModel):
    status_updated = pyqtSignal(str, str)

    def __init__(self, data=None):
        super().__init__()
        self.headers = ["Order ID", "Customer Name",
                        "Status", "Order Date", "Total Price"]
        self._raw_data = data or []
        self._data = self._convert_data(self._raw_data)

    def _convert_data(self, raw_data):
        converted = []
        for row in raw_data:
            if isinstance(row, dict):
                customer_name = "Unknown Customer"
                if row.get('customer_id'):
                    customer = get_customer_by_id(row['customer_id'])
                    if customer:
                        customer_name = customer.get(
                            'customer_name', customer_name)

                status_name = "Unknown Status"
                if row.get('order_status_id'):
                    status = get_order_status_by_id(row['order_status_id'])
                    if status:
                        status_name = status.get(
                            'order_status_name', status_name)

                order_date = row.get('order_date', '')
                if isinstance(order_date, datetime):
                    order_date = order_date.strftime('%Y-%m-%d %H:%M:%S')

                total_price = row.get('total_price', '')
                if isinstance(total_price, Decimal):
                    total_price = f"₱{float(total_price):.2f}"

                converted.append([
                    str(row.get('order_id', '')),
                    customer_name,
                    status_name,
                    str(order_date),
                    str(total_price)
                ])
            else:
                converted.append([str(item) for item in row])
        return converted

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            try:
                return self._data[index.row()][index.column()]
            except (IndexError, TypeError):
                return ""
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.headers[section]
            else:
                return str(section + 1)
        return None

    def flags(self, index):
        # Make all columns non-editable (removed status editing from table)
        return super().flags(index)

    def update_data(self, new_data):
        self.beginResetModel()
        self._raw_data = new_data
        self._data = self._convert_data(new_data)
        self.endResetModel()

    def get_order_data(self, row):
        try:
            if 0 <= row < len(self._raw_data):
                return self._raw_data[row]
            return None
        except (IndexError, TypeError):
            return None

    def get_order_id(self, row):
        try:
            order_data = self.get_order_data(row)
            if order_data:
                return int(order_data.get('order_id', 0))
            return None
        except (IndexError, ValueError, TypeError):
            return None


# -------- ORDER ITEMS TABLE MODEL --------
class OrderItemsTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self.headers = ["Order ID", "Service Name", "Quantity", "Price"]
        self._raw_data = data or []
        self._data = self._convert_data(self._raw_data)

    def _convert_data(self, raw_data):
        converted = []
        for row in raw_data:
            if isinstance(row, dict):
                service_name = "Unknown Service"
                if row.get('service_id'):
                    service = get_service_by_id(row['service_id'])
                    if service:
                        service_name = service.get(
                            'service_name', service_name)

                price = row.get('price', 0)
                if isinstance(price, Decimal):
                    price = f"₱ {float(price):.2f}"

                converted.append([
                    str(row.get('order_id', '')),
                    service_name,
                    str(row.get('quantity', '')),
                    str(price)
                ])
            else:
                converted.append([str(item) for item in row])
        return converted

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            try:
                return self._data[index.row()][index.column()]
            except (IndexError, TypeError):
                return ""
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.headers[section]
        return None

    def update_data(self, new_data):
        self.beginResetModel()
        self._raw_data = new_data
        self._data = self._convert_data(new_data)
        self.endResetModel()


# -------- FOR STATUS COMBOBOX IN TABLE --------
class StatusDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.statuses = get_all_order_statuses()

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        for status in self.statuses:
            combo.addItem(status["order_status_name"],
                          status["order_status_id"])
        return combo

    def setEditorData(self, editor, index):
        current_text = index.data(Qt.ItemDataRole.DisplayRole)
        idx = editor.findText(current_text)
        if idx >= 0:
            editor.setCurrentIndex(idx)

    def setModelData(self, editor, model, index):
        new_status_name = editor.currentText()
        model.setData(index, new_status_name, Qt.ItemDataRole.EditRole)


# -------- MAIN WINDOW --------
class AdminWindow(QMainWindow):
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Page - La Lavandera")
        self.setWindowIcon(QIcon("src/gui/a_logo.png"))
        self.setStyleSheet("background-color: #f9f9f9;")

        # Current selected order
        self.current_order_id = None
        self.is_deleting = False

        # Get orders
        try:
            orders_data = get_all_orders()
            print(f"✅ Loaded {len(orders_data)} orders from database")
        except Exception as e:
            print(f"❌ Error loading orders: {e}")
            import traceback
            traceback.print_exc()
            orders_data = []

        # Table model + view
        self.model = OrdersTableModel(orders_data)
        # Connect status update signal
        self.model.status_updated.connect(self.show_status_update_notification)
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.verticalHeader().setDefaultSectionSize(35)

        # Connect selection changed signal
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Configure table (removed status delegate - no editing in table anymore)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.setStyleSheet("""
            QTableView {
                background-color: #e6e6fa;
                border: 0px solid #122620;
                border-radius: 20px;
                font-size: 12px;
                padding: 10px; 
            }
            QTableView::item:hover {
                background-color: #d8cbef;            
            }
            QTableView::item:selected {
                background-color: #c9c9f6;
                color: black;
            }
            QHeaderView::section {
                background-color: #d8cbef;
                color: black;
                font-size: 13px;
                font-weight: normal;  
                padding: 10px;
                border: 0px solid #d8cbef;
            }
            QTableCornerButton::section {
                background-color: #d8cbef;
                border: 0px solid #c8c8d8;
            }
        """)

        self.initUI()
        self.showMaximized()

    # Show a notification when order status is updated (only if not deleting)
    def show_status_update_notification(self, old_status, new_status):
        if not self.is_deleting:
            QMessageBox.information(
                self,
                "Status Updated",
                f"Order status successfully changed from '{old_status}' to '{new_status}'!"
            )

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_vbox = QVBoxLayout(central_widget)

        # ---------- HEADER ZONE ----------
        header_vbox = QVBoxLayout()

        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back to Main")
        back_btn.setFixedSize(100, 30)
        back_btn.setStyleSheet("""
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

        back_btn.clicked.connect(self._on_back_clicked)
        back_btn.clicked.connect(self.close)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("src/gui/a_main_logo.png")
        desired_height = 50
        scaled_pixmap = pixmap.scaledToHeight(
            desired_height,
            Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setFixedHeight(desired_height)
        top_bar.addWidget(logo_label)

        header_vbox.addLayout(top_bar)

        # Buttons row
        hbox = QHBoxLayout()
        add_btn = QPushButton("Add Order")
        del_btn = QPushButton("Delete Order")

        add_btn.clicked.connect(self.open_order_form_page)
        del_btn.clicked.connect(self.delete_selected_order)

        self.buttons_style(add_btn)
        self.buttons_style(del_btn)

        hbox.addWidget(add_btn)
        hbox.addWidget(del_btn)
        header_vbox.addLayout(hbox)

        # Add table
        header_vbox.addWidget(self.table)

        outer_vbox.addLayout(header_vbox)

        # ---------- DETAIL CARDS ZONE ----------
        self.create_detail_cards(outer_vbox)

    def create_detail_cards(self, parent_layout):
        """Create the three horizontal cards for detailed information"""
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        # Card styling
        card_style = """
            QGroupBox {
                background-color: #e6e6fa;
                border: 2px solid #d8cbef;
                border-radius: 15px;
                font-size: 16px;
                font-weight: itatic;
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
                font-weight: normal;
                color: #122620;
            }
        """

        # ===== CUSTOMER INFO CARD =====
        customer_card = QGroupBox("Customer Information")
        customer_card.setStyleSheet(card_style)
        customer_card.setMaximumWidth(300)
        customer_layout = QVBoxLayout()
        customer_layout.setSpacing(8)

        # Customer ID
        cid_layout = QVBoxLayout()
        cid_layout.setSpacing(3)
        cid_title = QLabel("Customer ID")
        cid_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")
        self.customer_id_label = QLabel("-")
        self.customer_id_label.setStyleSheet(
            "font-size: 13px; color: #122620; padding: 4px; background-color: #e6e6fa; border-radius: 5px;")
        cid_layout.addWidget(cid_title)
        cid_layout.addWidget(self.customer_id_label)
        customer_layout.addLayout(cid_layout)

        # Customer Name
        cname_layout = QVBoxLayout()
        cname_layout.setSpacing(3)
        cname_title = QLabel("Customer Name")
        cname_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")
        self.customer_name_label = QLabel("-")
        self.customer_name_label.setStyleSheet(
            "font-size: 13px; color: #122620; padding: 4px; background-color: #e6e6fa; border-radius: 5px;")
        cname_layout.addWidget(cname_title)
        cname_layout.addWidget(self.customer_name_label)
        customer_layout.addLayout(cname_layout)

        # Contact Number
        contact_layout = QVBoxLayout()
        contact_layout.setSpacing(3)
        contact_title = QLabel("Contact Number")
        contact_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")
        self.customer_contact_label = QLabel("-")
        self.customer_contact_label.setStyleSheet(
            "font-size: 13px; color: #122620; padding: 4px; background-color: #e6e6fa; border-radius: 5px;")
        contact_layout.addWidget(contact_title)
        contact_layout.addWidget(self.customer_contact_label)
        customer_layout.addLayout(contact_layout)

        # Email
        email_layout = QVBoxLayout()
        email_layout.setSpacing(3)
        email_title = QLabel("Email")
        email_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")
        self.customer_email_label = QLabel("-")
        self.customer_email_label.setStyleSheet(
            "font-size: 13px; color: #122620; padding: 4px; background-color: #e6e6fa; border-radius: 5px;")
        email_layout.addWidget(email_title)
        email_layout.addWidget(self.customer_email_label)
        customer_layout.addLayout(email_layout)

        # Address (multi-line)
        address_layout = QVBoxLayout()
        address_layout.setSpacing(3)
        address_title = QLabel("Address")
        address_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")
        self.customer_address_text = QTextEdit()
        self.customer_address_text.setReadOnly(True)
        self.customer_address_text.setMaximumHeight(60)
        self.customer_address_text.setStyleSheet("""
            QTextEdit {
                font-size: 13px; 
                color: #122620; 
                padding: 4px; 
                background-color: #e6e6fa; 
                border: 0px solid #d8cbef;
                border-radius: 5px;
            }
        """)
        address_layout.addWidget(address_title)
        address_layout.addWidget(self.customer_address_text)
        customer_layout.addLayout(address_layout)

        customer_layout.addStretch()
        customer_card.setLayout(customer_layout)
        cards_layout.addWidget(customer_card)

        # ===== ORDER ITEMS CARD =====
        order_items_card = QGroupBox("Order Items")
        order_items_card.setStyleSheet(card_style)
        order_items_layout = QVBoxLayout()

        # Create table for order items
        self.order_items_model = OrderItemsTableModel([])
        self.order_items_table = QTableView()
        self.order_items_table.setModel(self.order_items_model)
        self.order_items_table.setAlternatingRowColors(True)
        self.order_items_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.order_items_table.setMaximumHeight(200)
        self.order_items_table.setStyleSheet("""
            QTableView {
                background-color: #e6e6fa;
                border: 0px solid #122620;
                border-radius: 5px;
                font-size: 12px;
                padding: 5px; 
            }
            QTableView::item:hover {
                background-color: #d8cbef;            
            }
            QTableView::item:selected {
                background-color: #c9c9f6;
                color: black;
            }
            QHeaderView::section {
                background-color: #d8cbef;
                color: black;
                font-size: 13px;
                font-weight: normal;  
                padding: 5px;
                border: 0px solid #d8cbef;
            }
            QTableCornerButton::section {
                background-color: #d8cbef;
                border: 0px solid #c8c8d8;
            }
        """)

        order_items_layout.addWidget(self.order_items_table)
        order_items_card.setLayout(order_items_layout)
        cards_layout.addWidget(order_items_card)

        # ===== PAYMENT INFO CARD (WITH ORDER STATUS) =====
        payment_card = QGroupBox("Payment & Order Information")
        payment_card.setStyleSheet(card_style)
        payment_layout = QFormLayout()

        self.total_price_label = QLabel("-")

        # Editable amount paid
        self.amount_paid_input = QDoubleSpinBox()
        self.amount_paid_input.setRange(0, 999999.99)
        self.amount_paid_input.setPrefix("₱ ")
        self.amount_paid_input.setDecimals(2)
        self.amount_paid_input.editingFinished.connect(
            self.on_amount_paid_editing_finished)

        self.amount_paid_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: transparent;;
                border: 1px solid #d8cbef;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
        """)

        self.payment_date_label = QLabel("-")

        # Payment method dropdown
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.currentIndexChanged.connect(
            self.on_payment_method_changed)
        self.payment_method_combo.setStyleSheet("""
            QComboBox {
                background-color: transparent;;
                border: 1px solid #d8cbef;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
        """)

        # Payment status dropdown
        self.payment_status_combo = QComboBox()
        self.payment_status_combo.currentIndexChanged.connect(
            self.on_payment_status_changed)
        self.payment_status_combo.setStyleSheet("""
            QComboBox {
                background-color: transparent;;
                border: 1px solid #d8cbef;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
        """)

        # Order status dropdown
        self.order_status_combo = QComboBox()
        self.order_status_combo.currentIndexChanged.connect(
            self.on_order_status_changed)
        self.order_status_combo.setStyleSheet("""
            QComboBox {
                background-color: transparent;;
                border: 1px solid #d8cbef;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
        """)

        total_title = QLabel("Total Price")
        total_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")
        self.total_price_label.setStyleSheet(
            "font-size: 13px; color: #122620; padding: 4px; background-color: #e6e6fa; border-radius: 5px;")

        amount_title = QLabel("Amount Paid")
        amount_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")

        payment_date_title = QLabel("Payment Date")
        payment_date_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")
        self.payment_date_label.setStyleSheet(
            "font-size: 13px; color: #122620; padding: 4px; background-color: #e6e6fa; border-radius: 5px;")

        method_title = QLabel("Payment Method")
        method_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")

        payment_status_title = QLabel("Payment Status")
        payment_status_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")

        order_status_title = QLabel("Order Status")
        order_status_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")

        payment_layout.addRow(total_title, self.total_price_label)
        payment_layout.addRow(amount_title, self.amount_paid_input)
        payment_layout.addRow(payment_date_title, self.payment_date_label)
        payment_layout.addRow(method_title, self.payment_method_combo)
        payment_layout.addRow(payment_status_title, self.payment_status_combo)
        payment_layout.addRow(order_status_title, self.order_status_combo)

        payment_card.setLayout(payment_layout)
        cards_layout.addWidget(payment_card)

        # Add cards to main layout
        parent_layout.addLayout(cards_layout)

        # Load dropdown options
        self.load_payment_dropdowns()
        self.load_order_status_dropdown()

    def load_payment_dropdowns(self):
        # Load payment methods
        try:
            methods = get_all_payment_methods()
            self.payment_method_combo.clear()
            for method in methods:
                self.payment_method_combo.addItem(
                    method['payment_method_name'],
                    method['payment_method_id']
                )
        except Exception as e:
            print(f"Error loading payment methods: {e}")

        # Load payment statuses
        try:
            statuses = get_all_payment_statuses()
            self.payment_status_combo.clear()
            for status in statuses:
                self.payment_status_combo.addItem(
                    status['payment_status_name'],
                    status['payment_status_id']
                )
        except Exception as e:
            print(f"Error loading payment statuses: {e}")

    def load_order_status_dropdown(self):
        """Load order statuses into dropdown"""
        try:
            statuses = get_all_order_statuses()
            self.order_status_combo.clear()
            for status in statuses:
                self.order_status_combo.addItem(
                    status['order_status_name'],
                    status['order_status_id']
                )
        except Exception as e:
            print(f"Error loading order statuses: {e}")

    def on_selection_changed(self, selected, deselected):
        """Handle table row selection changes"""
        indexes = selected.indexes()
        if indexes:
            row = indexes[0].row()
            self.load_order_details(row)

    def load_order_details(self, row):
        """Load all details for the selected order"""
        order_data = self.model.get_order_data(row)
        if not order_data:
            return

        order_id = order_data.get('order_id')
        self.current_order_id = order_id

        # Load customer info
        customer_id = order_data.get('customer_id')
        if customer_id:
            customer = get_customer_by_id(customer_id)
            if customer:
                self.customer_id_label.setText(
                    str(customer.get('customer_id', '-')))
                self.customer_name_label.setText(
                    customer.get('customer_name', '-'))

                contact = (customer.get('contact_number') or
                           customer.get('contact_no') or
                           customer.get('phone') or
                           customer.get('phone_number') or '-')
                self.customer_contact_label.setText(str(contact))

                email = customer.get('email') or customer.get(
                    'email_address') or '-'
                self.customer_email_label.setText(str(email))

                address = customer.get('address') or customer.get(
                    'customer_address') or '-'
                self.customer_address_text.setPlainText(str(address))

        # Load order status
        self.order_status_combo.blockSignals(True)
        order_status_id = order_data.get('order_status_id')
        for i in range(self.order_status_combo.count()):
            if self.order_status_combo.itemData(i) == order_status_id:
                self.order_status_combo.setCurrentIndex(i)
                break
        self.order_status_combo.blockSignals(False)

        # Load order items
        try:
            order_items = get_order_items_by_order(order_id)
            self.order_items_model.update_data(order_items)
        except Exception as e:
            print(f"Error loading order items: {e}")
            self.order_items_model.update_data([])

        # Load payment info
        try:
            payments = get_payments_by_order(order_id)
            if payments and len(payments) > 0:
                payment = payments[0]

                total_price = order_data.get('total_price', 0)
                if isinstance(total_price, Decimal):
                    self.total_price_label.setText(
                        f"₱{float(total_price):.2f}")
                else:
                    self.total_price_label.setText(f"₱{total_price:.2f}")

                # Block signals while setting values to avoid triggering updates
                self.amount_paid_input.blockSignals(True)
                amount_paid = payment.get('amount_paid', 0)
                if isinstance(amount_paid, Decimal):
                    self.amount_paid_input.setValue(float(amount_paid))
                else:
                    self.amount_paid_input.setValue(amount_paid)
                self.amount_paid_input.blockSignals(False)

                payment_date = payment.get('payment_date', '')
                if payment_date is None or payment_date == '':
                    self.payment_date_label.setText("-")
                elif isinstance(payment_date, datetime):
                    self.payment_date_label.setText(
                        payment_date.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    self.payment_date_label.setText(str(payment_date))

                # Set payment method
                self.payment_method_combo.blockSignals(True)
                method_id = payment.get('payment_method_id')
                for i in range(self.payment_method_combo.count()):
                    if self.payment_method_combo.itemData(i) == method_id:
                        self.payment_method_combo.setCurrentIndex(i)
                        break
                self.payment_method_combo.blockSignals(False)

                # Set payment status
                self.payment_status_combo.blockSignals(True)
                status_id = payment.get('payment_status_id')
                for i in range(self.payment_status_combo.count()):
                    if self.payment_status_combo.itemData(i) == status_id:
                        self.payment_status_combo.setCurrentIndex(i)
                        break
                self.payment_status_combo.blockSignals(False)
            else:
                self.clear_payment_info()
        except Exception as e:
            print(f"Error loading payment info: {e}")
            self.clear_payment_info()

    def clear_payment_info(self):
        self.total_price_label.setText("-")
        self.amount_paid_input.setValue(0)
        self.payment_date_label.setText("-")
        self.payment_method_combo.setCurrentIndex(0)
        self.payment_status_combo.setCurrentIndex(0)

    def on_amount_paid_editing_finished(self):
        if not self.current_order_id:
            return

        if self.is_deleting:
            return

        # Get the new value from the spinbox
        value = self.amount_paid_input.value()

        # Compare with the current database value before prompting
        try:
            payments = get_payments_by_order(self.current_order_id)
            if not payments:
                return
            payment = payments[0]
            old_value = float(payment.get('amount_paid', 0))
        except Exception as e:
            print(f"Error fetching payment: {e}")
            return

        if abs(value - old_value) < 0.01:
            return

        # Ask for confirmation
        confirm = QMessageBox.question(self, "Confirm Payment Update",
                                       f"Update amount paid to ₱{value:.2f}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm != QMessageBox.StandardButton.Yes:
            # revert to old value
            self.amount_paid_input.blockSignals(True)
            self.amount_paid_input.setValue(old_value)
            self.amount_paid_input.blockSignals(False)
            return

        # proceed with update
        try:
            payment_id = payment.get('payment_id')
            success = update_payment(
                payment_id,
                self.current_order_id,
                Decimal(str(value)),
                payment.get('payment_date'),
                payment.get('payment_method_id'),
                payment.get('payment_status_id')
            )

            if success:
                print(f"✅ Amount paid updated to ₱{value:.2f}")
            else:
                print("❌ Failed to update amount paid")
                QMessageBox.warning(
                    self, "Error", "Failed to update amount paid")

        except Exception as e:
            print(f"Error updating amount paid: {e}")
            QMessageBox.critical(
                self, "Error", f"Error updating amount paid:\n{e}")

    def on_payment_method_changed(self, index):
        if not self.current_order_id or index < 0:
            return

        if self.is_deleting:
            return

        method_name = self.payment_method_combo.currentText()
        confirm = QMessageBox.question(
            self,
            "Confirm Payment Method Update",
            f"Change payment method to '{method_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            try:
                payments = get_payments_by_order(self.current_order_id)
                if payments and len(payments) > 0:
                    payment = payments[0]
                    method_id = payment.get('payment_method_id')
                    self.payment_method_combo.blockSignals(True)
                    for i in range(self.payment_method_combo.count()):
                        if self.payment_method_combo.itemData(i) == method_id:
                            self.payment_method_combo.setCurrentIndex(i)
                            break
                    self.payment_method_combo.blockSignals(False)
            except Exception as e:
                print(f"Error reverting payment method: {e}")
            return

        try:
            payments = get_payments_by_order(self.current_order_id)
            if payments and len(payments) > 0:
                payment = payments[0]
                payment_id = payment.get('payment_id')
                method_id = self.payment_method_combo.itemData(index)

                success = update_payment(payment_id, self.current_order_id, payment.get(
                    'amount_paid'), payment.get('payment_date'), method_id, payment.get('payment_status_id'))

                if success:
                    QMessageBox.information(
                        self, "Success", f"Payment method updated to '{method_name}'")
                    print(f"✅ Updated payment method")
                else:
                    print("❌ Failed to update payment method")
                    QMessageBox.warning(
                        self, "Error", "Failed to update payment method")
        except Exception as e:
            print(f"Error updating payment method: {e}")
            QMessageBox.critical(
                self, "Error", f"Error updating payment method:\n{e}")

    def on_payment_status_changed(self, index):
        if not self.current_order_id or index < 0:
            return

        # Don't show popup during deletion
        if self.is_deleting:
            return

        status_name = self.payment_status_combo.currentText()
        confirm = QMessageBox.question(self, "Confirm Payment Status Update",
                                       f"Change payment status to '{status_name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm != QMessageBox.StandardButton.Yes:
            try:
                payments = get_payments_by_order(self.current_order_id)
                if payments and len(payments) > 0:
                    payment = payments[0]
                    status_id = payment.get('payment_status_id')
                    self.payment_status_combo.blockSignals(True)
                    for i in range(self.payment_status_combo.count()):
                        if self.payment_status_combo.itemData(i) == status_id:
                            self.payment_status_combo.setCurrentIndex(i)
                            break
                    self.payment_status_combo.blockSignals(False)
            except Exception as e:
                print(f"Error reverting payment status: {e}")
            return

        current_row = self.table.selectionModel().selectedRows()[0].row(
        ) if self.table.selectionModel().selectedRows() else None

        try:
            payments = get_payments_by_order(self.current_order_id)
            if payments and len(payments) > 0:
                payment = payments[0]
                payment_id = payment.get('payment_id')
                status_id = self.payment_status_combo.itemData(index)

                # Get order data for total price
                order_data = self.model.get_order_data(current_row)
                total_price = order_data.get('total_price', 0)
                if isinstance(total_price, Decimal):
                    total_price = float(total_price)

                # Auto-set values based on status
                status_text = status_name.lower().strip()

                if status_text == "paid":
                    payment_date = datetime.now()
                    amount_paid = Decimal(str(total_price))
                elif status_text in ["pending", "unpaid", "cancelled"]:
                    payment_date = None
                    amount_paid = payment.get('amount_paid')
                elif status_text == "refunded":
                    payment_date = None
                    amount_paid = Decimal('0')
                else:
                    payment_date = payment.get('payment_date')
                    amount_paid = payment.get('amount_paid')

                success = update_payment(
                    payment_id,
                    self.current_order_id,
                    amount_paid,
                    payment_date,
                    payment.get('payment_method_id'),
                    status_id
                )

                if success:
                    if payment_date:
                        self.payment_date_label.setText(
                            payment_date.strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        self.payment_date_label.setText("-")

                    self.amount_paid_input.blockSignals(True)
                    self.amount_paid_input.setValue(float(amount_paid))
                    self.amount_paid_input.blockSignals(False)

                    if status_text == "paid":
                        self.auto_update_order_status_to_queueing()

                    self.model.update_data(get_all_orders())
                    if current_row is not None:
                        self.table.selectRow(current_row)

                    QMessageBox.information(
                        self, "Success", f"Payment status updated to '{status_name}'")
                    print(f"✅ Updated payment status to {status_name}")
                else:
                    print("❌ Failed to update payment status")
                    QMessageBox.warning(
                        self, "Error", "Failed to update payment status")
        except Exception as e:
            print(f"Error updating payment status: {e}")
            QMessageBox.critical(
                self, "Error", f"Error updating payment status:\n{e}")

    def auto_update_order_status_to_queueing(self):
        try:
            current_index = self.order_status_combo.currentIndex()
            current_status_name = self.order_status_combo.currentText().lower().strip()

            if current_status_name == "pending payment":
                for i in range(self.order_status_combo.count()):
                    if self.order_status_combo.itemText(i).lower().strip() == "queueing":
                        self.order_status_combo.blockSignals(True)
                        self.order_status_combo.setCurrentIndex(i)
                        self.order_status_combo.blockSignals(False)

                        # Update database
                        current_row = self.table.selectionModel().selectedRows()[0].row(
                        ) if self.table.selectionModel().selectedRows() else None
                        order_data = self.model.get_order_data(current_row)
                        status_id = self.order_status_combo.itemData(i)

                        update_order(
                            self.current_order_id, order_data["customer_id"], status_id, order_data["order_date"], order_data["total_price"])

                        # Update table display and reselect
                        self.model.update_data(get_all_orders())
                        if current_row is not None:
                            self.table.selectRow(current_row)

                        print("✅ Auto-updated order status to Queueing")
                        break
        except Exception as e:
            print(f"Error auto-updating order status: {e}")

    def on_order_status_changed(self, index):
        if not self.current_order_id or index < 0:
            return

        if self.is_deleting:
            return

        status_name = self.order_status_combo.currentText()
        confirm = QMessageBox.question(self, "Confirm Order Status Update",
                                       f"Change order status to '{status_name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm != QMessageBox.StandardButton.Yes:
            try:
                # Revert to original value
                row = self.table.selectionModel().selectedRows()[0].row(
                ) if self.table.selectionModel().selectedRows() else None
                if row is not None:
                    order_data = self.model.get_order_data(row)
                    order_status_id = order_data.get('order_status_id')
                    self.order_status_combo.blockSignals(True)
                    for i in range(self.order_status_combo.count()):
                        if self.order_status_combo.itemData(i) == order_status_id:
                            self.order_status_combo.setCurrentIndex(i)
                            break
                    self.order_status_combo.blockSignals(False)
            except Exception as e:
                print(f"Error reverting order status: {e}")
            return

        current_row = self.table.selectionModel().selectedRows()[0].row(
        ) if self.table.selectionModel().selectedRows() else None

        try:
            order_data = self.model.get_order_data(current_row)
            status_id = self.order_status_combo.itemData(index)

            success = update_order(
                self.current_order_id,
                order_data["customer_id"],
                status_id,
                order_data["order_date"],
                order_data["total_price"]
            )

            if success:
                self.model.update_data(get_all_orders())
                if current_row is not None:
                    self.table.selectRow(current_row)

                status_text = status_name.lower().strip()
                if status_text == "cancelled":
                    self.auto_refund_payment()

                QMessageBox.information(
                    self, "Success", f"Order status updated to '{status_name}'")
                print(f"✅ Updated order status to {status_name}")
            else:
                print("❌ Failed to update order status")
                QMessageBox.warning(
                    self, "Error", "Failed to update order status")
        except Exception as e:
            print(f"Error updating order status: {e}")
            QMessageBox.critical(
                self, "Error", f"Error updating order status:\n{e}")

    def auto_refund_payment(self):
        try:
            payments = get_payments_by_order(self.current_order_id)
            if payments and len(payments) > 0:
                payment = payments[0]
                payment_id = payment.get('payment_id')

                # Find "Refunded" status
                refunded_status_id = None
                for i in range(self.payment_status_combo.count()):
                    if self.payment_status_combo.itemText(i).lower().strip() == "refunded":
                        refunded_status_id = self.payment_status_combo.itemData(
                            i)
                        break

                if refunded_status_id:
                    success = update_payment(payment_id, self.current_order_id, Decimal(
                        '0'), None, payment.get('payment_method_id'), refunded_status_id)

                    if success:
                        # Update UI
                        self.amount_paid_input.blockSignals(True)
                        self.amount_paid_input.setValue(0)
                        self.amount_paid_input.blockSignals(False)

                        self.payment_date_label.setText("-")

                        self.payment_status_combo.blockSignals(True)
                        for i in range(self.payment_status_combo.count()):
                            if self.payment_status_combo.itemData(i) == refunded_status_id:
                                self.payment_status_combo.setCurrentIndex(i)
                                break
                        self.payment_status_combo.blockSignals(False)

                        print("✅ Auto-refunded payment (set to ₱0)")
        except Exception as e:
            print(f"Error auto-refunding payment: {e}")

    def _on_back_clicked(self):
        self.back_requested.emit()

    def closeEvent(self, event):
        super().closeEvent(event)

    def open_order_form_page(self):
        dialog = AddOrderDialog(self)
        if dialog.exec():
            self.model.update_data(get_all_orders())

    def delete_selected_order(self):
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "No Selection",
                                "Please select an order to delete.")
            return

        row = indexes[0].row()
        order_data = self.model.get_order_data(row)
        order_id = order_data.get("order_id")
        customer_id = order_data.get("customer_id")

        if not order_id:
            QMessageBox.warning(
                self, "Error", "Could not find Order ID for the selected row.")
            return

        confirm = QMessageBox.question(
            self, "Confirm Delete", f"Are you sure you want to delete Order ID {order_id}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm != QMessageBox.StandardButton.Yes:
            return

        # Set flag to suppress notifications during deletion
        self.is_deleting = True

        try:
            # Delete payments
            from models.payment import get_payments_by_order, delete_payment
            payments = get_payments_by_order(order_id)
            for p in payments:
                delete_payment(p["payment_id"])

            # Delete order items
            from models.order_item import get_order_items_by_order, delete_order_item
            order_items = get_order_items_by_order(order_id)
            for item in order_items:
                delete_order_item(item["order_item_id"])

            # Delete order itself
            success = delete_order(order_id)

            # Delete customer if they have no other orders
            if customer_id:
                from models.order import get_all_orders
                from models.customer import delete_customer
                remaining_orders = [
                    o for o in get_all_orders() if o["customer_id"] == customer_id]
                if len(remaining_orders) == 0:
                    delete_customer(customer_id)
                    print(
                        f"🧹 Customer ID {customer_id} deleted (no remaining orders)")

            if success:
                QMessageBox.information(
                    self, "Deleted", f"Order ID {order_id} has been deleted successfully.")
                self.model.update_data(get_all_orders())
                self.clear_payment_info()
                self.customer_id_label.setText("-")
                self.customer_name_label.setText("-")
                self.customer_contact_label.setText("-")
                self.customer_email_label.setText("-")
                self.customer_address_text.setPlainText("-")
                self.order_items_model.update_data([])
            else:
                QMessageBox.warning(
                    self, "Failed", "Failed to delete order from database.")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred while deleting the order:\n{e}")
        finally:
            self.is_deleting = False

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


# Main execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    sys.exit(app.exec())
