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
    def __init__(self, data=None):
        super().__init__()
        self.headers = ["Order ID", "Customer Name",
                        "Status", "Order Date", "Total Price"]
        self._raw_data = data or []
        self._data = self._convert_data(self._raw_data)

    def _convert_data(self, raw_data):
        """Convert dict rows with MySQL data types to string format for table display"""
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
        base_flags = super().flags(index)
        if index.column() == 2:  # Status column
            return base_flags | Qt.ItemFlag.ItemIsEditable
        return base_flags

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        row = index.row()
        col = index.column()

        if col == 2:  # Status column
            order_id = self.get_order_id(row)
            order_data = self.get_order_data(row)

            # find status_id from name
            all_statuses = get_all_order_statuses()
            status_id = None
            for s in all_statuses:
                if s["order_status_name"] == value:
                    status_id = s["order_status_id"]
                    break

            if order_id and order_data and status_id:
                success = update_order(
                    order_id,
                    order_data["customer_id"],
                    status_id,
                    order_data["order_date"],
                    order_data["total_price"]
                )
                if success:
                    self._data[row][col] = value
                    self.dataChanged.emit(
                        index, index, [Qt.ItemDataRole.DisplayRole])
                    return True
        return False

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
        self.table = QTableView()
        self.table.setModel(self.model)

        # Connect selection changed signal
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Set up dropdown editor for Status column
        status_delegate = StatusDelegate(self.table)
        self.table.setItemDelegateForColumn(2, status_delegate)

        # Configure table
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
        customer_card.setMaximumWidth(300)  # Make card narrower
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

        # ===== PAYMENT INFO CARD =====
        payment_card = QGroupBox("Payment Information")
        payment_card.setStyleSheet(card_style)
        payment_layout = QFormLayout()

        self.total_price_label = QLabel("-")

        # Editable amount paid
        self.amount_paid_input = QDoubleSpinBox()
        self.amount_paid_input.setRange(0, 999999.99)
        self.amount_paid_input.setPrefix("₱ ")
        self.amount_paid_input.setDecimals(2)
        self.amount_paid_input.valueChanged.connect(
            self.on_amount_paid_changed)
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

        status_title = QLabel("Payment Status")
        status_title.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #666; background-color: transparent;")

        payment_layout.addRow(total_title, self.total_price_label)
        payment_layout.addRow(amount_title, self.amount_paid_input)
        payment_layout.addRow(payment_date_title, self.payment_date_label)
        payment_layout.addRow(method_title, self.payment_method_combo)
        payment_layout.addRow(status_title, self.payment_status_combo)

        payment_card.setLayout(payment_layout)
        cards_layout.addWidget(payment_card)

        # Add cards to main layout
        parent_layout.addLayout(cards_layout)

        # Load dropdown options
        self.load_payment_dropdowns()

    def load_payment_dropdowns(self):
        """Load payment methods and statuses into dropdowns"""
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
                # Debug: print what columns we actually have
                print(f"Customer data keys: {customer.keys()}")
                print(f"Customer data: {customer}")

                self.customer_id_label.setText(
                    str(customer.get('customer_id', '-')))
                self.customer_name_label.setText(
                    customer.get('customer_name', '-'))

                # Try different possible column names
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
                payment = payments[0]  # Get first payment

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
                if isinstance(payment_date, datetime):
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
                # No payment found
                self.clear_payment_info()
        except Exception as e:
            print(f"Error loading payment info: {e}")
            self.clear_payment_info()

    def clear_payment_info(self):
        """Clear payment information fields"""
        self.total_price_label.setText("-")
        self.amount_paid_input.setValue(0)
        self.payment_date_label.setText("-")
        self.payment_method_combo.setCurrentIndex(0)
        self.payment_status_combo.setCurrentIndex(0)

    def on_amount_paid_changed(self, value):
        """Handle amount paid changes"""
        if not self.current_order_id:
            return

        try:
            payments = get_payments_by_order(self.current_order_id)
            if payments and len(payments) > 0:
                payment = payments[0]
                payment_id = payment.get('payment_id')

                # Update payment in database
                success = update_payment(
                    payment_id,
                    self.current_order_id,
                    Decimal(str(value)),
                    payment.get('payment_date'),
                    payment.get('payment_method_id'),
                    payment.get('payment_status_id')
                )

                if success:
                    print(f"✅ Updated amount paid to {value}")
                else:
                    print("❌ Failed to update amount paid")
        except Exception as e:
            print(f"Error updating amount paid: {e}")

    def on_payment_method_changed(self, index):
        """Handle payment method changes"""
        if not self.current_order_id or index < 0:
            return

        try:
            payments = get_payments_by_order(self.current_order_id)
            if payments and len(payments) > 0:
                payment = payments[0]
                payment_id = payment.get('payment_id')
                method_id = self.payment_method_combo.itemData(index)

                success = update_payment(
                    payment_id,
                    self.current_order_id,
                    payment.get('amount_paid'),
                    payment.get('payment_date'),
                    method_id,
                    payment.get('payment_status_id')
                )

                if success:
                    print(f"✅ Updated payment method")
                else:
                    print("❌ Failed to update payment method")
        except Exception as e:
            print(f"Error updating payment method: {e}")

    def on_payment_status_changed(self, index):
        """Handle payment status changes"""
        if not self.current_order_id or index < 0:
            return

        try:
            payments = get_payments_by_order(self.current_order_id)
            if payments and len(payments) > 0:
                payment = payments[0]
                payment_id = payment.get('payment_id')
                status_id = self.payment_status_combo.itemData(index)

                success = update_payment(
                    payment_id,
                    self.current_order_id,
                    payment.get('amount_paid'),
                    payment.get('payment_date'),
                    payment.get('payment_method_id'),
                    status_id
                )

                if success:
                    print(f"✅ Updated payment status")
                else:
                    print("❌ Failed to update payment status")
        except Exception as e:
            print(f"Error updating payment status: {e}")

    def _on_back_clicked(self):
        self.back_requested.emit()

    def closeEvent(self, event):
        # self.back_requested.emit()
        super().closeEvent(event)

    def open_order_form_page(self):
        dialog = AddOrderDialog(self)
        if dialog.exec():
            self.model.update_data(get_all_orders())

    def delete_selected_order(self):
        """Delete the selected order and related data (payments, items, and customer if no other orders)"""
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
            self,
            "Confirm Delete",
            f"Are you sure you want to delete Order ID {order_id}, its related records, "
            "and the customer (if they have no other orders)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            # Step 1: Delete payments
            from models.payment import get_payments_by_order, delete_payment
            payments = get_payments_by_order(order_id)
            for p in payments:
                delete_payment(p["payment_id"])

            # Step 2: Delete order items
            from models.order_item import get_order_items_by_order, delete_order_item
            order_items = get_order_items_by_order(order_id)
            for item in order_items:
                delete_order_item(item["order_item_id"])

            # Step 3: Delete order itself
            success = delete_order(order_id)

            # Step 4: Delete customer if they have no other orders
            if customer_id:
                from models.order import get_all_orders
                from models.customer import delete_customer
                remaining_orders = [
                    o for o in get_all_orders() if o["customer_id"] == customer_id
                ]
                if len(remaining_orders) == 0:
                    delete_customer(customer_id)
                    print(
                        f"🧹 Customer ID {customer_id} deleted (no remaining orders)")

            if success:
                QMessageBox.information(
                    self,
                    "Deleted",
                    f"Order ID {order_id} (and customer if applicable) has been deleted."
                )
                # Refresh table + clear info
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
