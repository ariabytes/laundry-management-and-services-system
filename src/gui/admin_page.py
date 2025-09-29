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
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QAbstractTableModel, QModelIndex
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QTableView, QMessageBox, QInputDialog, QHeaderView, QScrollArea, QFrame,
                             QLineEdit, QComboBox, QTextEdit, QDateEdit, QDoubleSpinBox, QSpinBox, QGroupBox, QFormLayout, QGridLayout, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem, QCheckBox, QStyledItemDelegate)

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
# -------- TABLE --------

# -------- FOR STATUS COMBOBOX IN TABLE --------


class StatusDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        # preload all statuses from DB
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
# -------- STATUS COMBOBOX IN TABLE --------


# -------- MAIN WINDOW --------
class AdminWindow(QMainWindow):
    back_requested = pyqtSignal()  # signal MainWindow listens to

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Page - La Lavandera")
        self.setWindowIcon(QIcon("src/gui/a_logo.png"))

        self.setStyleSheet("background-color: #f9f9f9;")

        # ---- FOR TABLE ----
        # Get orders with error handling
        try:
            orders_data = get_all_orders()
            print(f"✅ Loaded {len(orders_data)} orders from database")
            if orders_data:
                print(f"Sample order: {orders_data[0]}")
        except Exception as e:
            print(f"❌ Error loading orders: {e}")
            import traceback
            traceback.print_exc()
            orders_data = []

        # Table model + view
        print("Creating table model...")
        self.model = OrdersTableModel(orders_data)
        self.table = QTableView()
        self.table.setModel(self.model)

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
                font-size: 14px;
                padding: 15px; 
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
                font-size: 15px;
                font-weight: normal;  
                padding: 15px;
                border: 0px solid #d8cbef;
            }
            QHeaderView::section:pressed {
                font-weight: normal; 
            }
            QTableCornerButton::section {
                background-color: #d8cbef;
                border: 0px solid #c8c8d8;
            }
        """)

        # Call UI setup here
        self.initUI()

        # BIG
        self.showMaximized()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # ---- MAIN OUTER LAYOUT ----
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
        # Close admin page to go back to main
        back_btn.clicked.connect(self.close)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()

        # Logo on the right
        logo_label = QLabel()
        pixmap = QPixmap("src/gui/a_main_logo.png")

        # Set a fixed height (e.g. 50px) and scale width proportionally
        desired_height = 50
        scaled_pixmap = pixmap.scaledToHeight(
            desired_height,
            Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(scaled_pixmap)
        # only fix height, width auto-adjusts
        logo_label.setFixedHeight(desired_height)
        top_bar.addWidget(logo_label)

        header_vbox.addLayout(top_bar)
        outer_vbox.addLayout(header_vbox)

        main_vbox = QVBoxLayout()
        main_vbox.addStretch(1)

        outer_vbox.addLayout(main_vbox)

        # Buttons row
        hbox = QHBoxLayout()
        add_btn = QPushButton("Add Order")
        del_btn = QPushButton("Delete Order")
        refresh_btn = QPushButton("Refresh Orders")

        self.buttons_style(add_btn)
        self.buttons_style(del_btn)
        self.buttons_style(refresh_btn)

        hbox.addWidget(add_btn)
        hbox.addWidget(del_btn)
        hbox.addWidget(refresh_btn)
        header_vbox.addLayout(hbox)

        # # Add header zone to outer layout
        # outer_vbox.addLayout(header_vbox)

        header_vbox.addWidget(self.table)


# ---------- MAIN WINDOW METHODS ----------
    # FOR BACK TO MAIN

    def _on_back_clicked(self):
        # ask MainWindow to handle going back
        self.back_requested.emit()

    def closeEvent(self, event):
        # If user closes the admin window via the X button, also request back
        self.back_requested.emit()
        super().closeEvent(event)

    # FOR BUTTONS STYLE HEHE

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
# -------- MAIN WINDOW --------


# Main execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    sys.exit(app.exec())
