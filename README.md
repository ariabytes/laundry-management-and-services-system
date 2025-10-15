# La Lavandera - Laundry Monitoring and Services System

## Introduction

The **La Lavandera Laundry Monitoring and Services System** is a desktop application built with Python and PyQt6, featuring a MySQL backend. It streamlines laundry shop operations by enabling administrators to manage orders, payments, and customer information efficiently, while allowing clients to conveniently track their laundry status using a unique Order ID.

---

## Problem Statement

Local laundry shops often rely on manual, paper-based processes for managing orders, receipts, and payments. This results in:

- Misplaced orders and lost paperwork
- Inaccurate time estimates for completion
- Billing errors and payment disputes
- Inefficient record-keeping for both business owners and clients
- Difficulty tracking order status in real-time

---

## Target Users

- **Laundry shop owners and staff** - Full admin access for comprehensive order and customer management
- **Laundry shop clients** - Self-service order tracking and status inquiry
- **Walk-in customers** - Service information browsing and pricing details

---

## Features

### Admin Features

- **Secure Authentication System** - Password-protected admin login
- **Comprehensive Order Management** - Create, view, update, and delete orders
- **Real-time Order Tracking** - Monitor order status from pending to completed
- **Customer Information Management** - Store and manage customer details
- **Payment Processing** - Track payments with multiple methods (Cash, Card, E-Wallet, Bank Transfer)
- **Payment Status Management** - Handle pending, partial, paid, failed, and refunded payments
- **Order Status Workflow** - Manage orders through stages: Pending Payment → Queueing → Washing/Cleaning → Finishing Up → Ready for Pickup → Completed
- **Auto-refund on Cancellation** - Automatically handle refunds when orders are cancelled
- **Service Catalog** - View all available services grouped by category

### Customer Features

- **Order Tracking Interface** - Track laundry status using Order ID
- **Order Details View** - See complete order information including items and pricing
- **Payment Information** - View payment status and amount paid
- **Service Price List** - Browse available services and pricing

### System Features

- **Data Validation** - Comprehensive validation for customer info, orders, and payments
- **Business Logic Enforcement** - Automatic status updates based on payment
- **Database Integrity** - Cascading deletes and referential integrity
- **Professional UI** - Clean, modern interface with custom styling
- **Responsive Design** - Intuitive navigation and user feedback

---

## 🎓 OOP Concepts Applied

### 1. **Encapsulation**

- **Customer Class**: Encapsulates customer data and operations

  ```python
  class Customer:
      def __init__(self, customer_id, name, phone, email, address):
          self.customer_id = customer_id  # Private data
          self.name = name
          # ... other attributes

      def save(self):  # Public method
          # Encapsulates database logic

      def to_dict(self):  # Data transformation
          # Returns dictionary representation
  ```

- **Database Connection**: Encapsulates connection management
  ```python
  @contextmanager
  def db_cursor(conn, dictionary=True):
      cursor = conn.cursor(dictionary=dictionary)
      try:
          yield cursor
      finally:
          cursor.close()
  ```

### 2. **Inheritance**

- **Payment Status Hierarchy**: Base class with specialized subclasses

  ```python
  class PaymentStatus:  # Base class
      def get_payment_date(self):
          return None

  class PaidStatus(PaymentStatus):  # Derived class
      def get_payment_date(self):
          return datetime.now()  # Override behavior

  class RefundedStatus(PaymentStatus):  # Another derived class
      def get_amount_paid(self, total_price):
          return Decimal("0")  # Different behavior
  ```

### 3. **Polymorphism**

- **Method Overriding**: Different payment statuses have different behaviors

  ```python
  status = PaymentStatusFactory.create("Paid")
  payment_date = status.get_payment_date()  # Returns datetime.now()

  status = PaymentStatusFactory.create("Pending")
  payment_date = status.get_payment_date()  # Returns None
  ```

- **Interface Consistency**: All status classes implement the same methods but with different logic

### 4. **Abstraction**

- **Validator Classes**: Abstract away complex validation logic

  ```python
  class OrderValidator:
      def validate_customer_info(self, name, phone, email, address):
          # Complex validation hidden from caller

      def validate_order_items(self, items):
          # Business rules abstracted
  ```

- **Payment Processor**: Abstracts payment calculations
  ```python
  class PaymentProcessor:
      @staticmethod
      def calculate_total(order_items):
          # Calculation logic abstracted

      @staticmethod
      def determine_payment_status_from_amount(amount_paid, total_price):
          # Decision logic hidden
  ```

### 5. **Factory Pattern**

- **PaymentStatusFactory**: Creates appropriate status objects
  ```python
  class PaymentStatusFactory:
      @classmethod
      def create(cls, status_name):
          status_key = status_name.lower().strip()
          status_class = cls._status_map.get(status_key)
          if status_class:
              return status_class()
          return PaymentStatus(status_name)
  ```

### 6. **Single Responsibility Principle**

- Each class has a single, well-defined purpose:
  - `Customer` - Manages customer data
  - `OrderValidator` - Validates order-related data
  - `PaymentProcessor` - Handles payment calculations
  - `OrderStatusManager` - Manages order status transitions

### 7. **Composition**

- GUI components composed of multiple parts:
  ```python
  class AdminWindow:
      def __init__(self):
          self.model = OrdersTableModel()  # Has-a relationship
          self.table = QTableView()         # Has-a relationship
          self.validator = OrderValidator() # Has-a relationship
  ```

---

## Database Overview

### Database Schema

**Core Tables:**

- **`admin`** - Staff authentication and credentials
- **`customers`** - Customer personal information
- **`orders`** - Order records with status and totals
- **`order_items`** - Individual services per order
- **`payments`** - Payment transactions and records

**Reference Tables:**

- **`categories`** - Service groupings (Standard, Specialized, Dry Cleaning, Add Ons)
- **`services`** - Available laundry services with pricing
- **`order_statuses`** - Order workflow stages
- **`payment_statuses`** - Payment states (Pending, Partial, Paid, Failed, Refunded)
- **`payment_methods`** - Payment options (Cash, Card, E-Wallet, Bank Transfer)

### Service Categories

1. **Standard** - Machine Wash & Dry, Hand Wash & Dry
2. **Specialized** - Carpet, Comforter, Bedsheets, Stuffed Toys
3. **Dry Cleaning** - Barong, Blouse, Pants, Jacket, Suits, Gowns
4. **Add Ons** - Express Service, Delivery, Folding, Pressing, Stain Removal

---

## Entity-Relationship Diagram

```mermaid
erDiagram
    ADMIN {
        int admin_id PK
        varchar username UK
        varchar password
        varchar name
        varchar email
        datetime created_at
    }

    CUSTOMERS {
        int customer_id PK
        varchar customer_name
        varchar customer_phone
        varchar customer_email
        varchar customer_address
    }

    ORDERS {
        int order_id PK
        int customer_id FK
        int order_status_id FK
        datetime order_date
        decimal total_price
    }

    ORDER_ITEMS {
        int order_item_id PK
        int order_id FK
        int service_id FK
        int quantity
        decimal price
    }

    SERVICES {
        int service_id PK
        int category_id FK
        varchar service_name
        decimal min_price
        decimal max_price
        varchar price_unit
        text service_notes
    }

    CATEGORIES {
        int category_id PK
        varchar category_name
    }

    ORDER_STATUSES {
        int order_status_id PK
        varchar order_status_name
    }

    PAYMENTS {
        int payment_id PK
        int order_id FK
        int payment_method_id FK
        int payment_status_id FK
        decimal amount_paid
        datetime payment_date
    }

    PAYMENT_METHODS {
        int payment_method_id PK
        varchar payment_method_name
    }

    PAYMENT_STATUSES {
        int payment_status_id PK
        varchar payment_status_name
    }

    CUSTOMERS ||--o{ ORDERS : "places"
    ORDERS ||--o{ ORDER_ITEMS : "contains"
    ORDERS }o--|| ORDER_STATUSES : "has"
    ORDERS ||--o{ PAYMENTS : "paid_by"

    ORDER_ITEMS }o--|| SERVICES : "uses"
    SERVICES }o--|| CATEGORIES : "belongs_to"

    PAYMENTS }o--|| PAYMENT_METHODS : "uses"
    PAYMENTS }o--|| PAYMENT_STATUSES : "has"
```

---

## Sequence Diagram – Add Order Flow

```mermaid
sequenceDiagram
    participant Admin
    participant AdminWindow
    participant OrderDialog
    participant Validator
    participant Database

    Admin->>AdminWindow: Click "Add Order"
    AdminWindow->>OrderDialog: Open AddOrderDialog()

    OrderDialog->>Database: Load customers
    Database-->>OrderDialog: Customer list

    OrderDialog->>Database: Load services
    Database-->>OrderDialog: Service list with categories

    OrderDialog-->>Admin: Display form

    Admin->>OrderDialog: Fill customer info
    Admin->>OrderDialog: Select services & quantities
    OrderDialog->>OrderDialog: Calculate total price

    Admin->>OrderDialog: Enter payment details
    OrderDialog->>OrderDialog: Auto-determine payment status

    Admin->>OrderDialog: Click "Add Order"

    OrderDialog->>Validator: validate_customer_info()
    Validator-->>OrderDialog: Valid

    OrderDialog->>Validator: validate_order_items()
    Validator-->>OrderDialog: Valid

    OrderDialog->>Validator: validate_payment()
    Validator-->>OrderDialog: Valid

    OrderDialog->>Database: INSERT customer
    Database-->>OrderDialog: customer_id

    OrderDialog->>Database: INSERT order
    Database-->>OrderDialog: order_id

    loop For each service
        OrderDialog->>Database: INSERT order_item
    end

    OrderDialog->>Database: INSERT payment

    OrderDialog-->>AdminWindow: Success
    AdminWindow->>AdminWindow: Refresh orders list
    AdminWindow-->>Admin: Show updated orders
```

---

## Technologies Used

- **Python 3.8+** - Core application development and business logic
- **PyQt6** - Modern cross-platform GUI framework
- **MySQL 8.0** - Relational database management system
- **mysql-connector-python** - Python MySQL database adapter
- **XAMPP** - Local development environment (Apache + MySQL)
- **Decimal** - Precise monetary calculations

---
## 🧺 Project Structure

```
LaundrySystem/
├── src/
│   ├── db/                              # 🗄️ Database Layer
│   │   ├── __init__.py                  # Package marker
│   │   ├── connection.py                # Database connection & context manager
│   │   └── db_laundry.sql               # Database schema & initial data
│   │
│   ├── gui/                             # 🖥️ User Interface Layer
│   │   ├── __init__.py                  # Package marker
│   │   ├── main_window.py               # Main application window & entry point
│   │   ├── login_page.py                # Admin authentication dialog
│   │   ├── admin_page.py                # Order management interface (main admin view)
│   │   ├── order_form_page.py           # Add/Edit order dialog with validation
│   │   ├── track_order_page.py          # Customer order tracking interface
│   │   ├── services_page.py             # Service catalog display
│   │   ├── a_logo.png                   # Application icon (16x16, 32x32)
│   │   └── a_main_logo.png              # Main logo banner image
│   │
│   └── models/                          # 📊 Business Logic & Data Layer
│       ├── __init__.py                  # Package marker
│       ├── admin.py                     # Admin authentication CRUD
│       ├── customer_class.py            # Customer class with OOP methods
│       ├── order.py                     # Order CRUD operations
│       ├── order_item.py                # Order items management
│       ├── order_status.py              # Order status CRUD
│       ├── order_validator.py           # Business logic validators (OOP)
│       ├── service.py                   # Service catalog CRUD
│       ├── category.py                  # Service categories CRUD
│       ├── payment.py                   # Payment CRUD operations
│       ├── payment_method.py            # Payment methods CRUD
│       ├── payment_status.py            # Payment status CRUD
│       └── status_factory.py            # Factory pattern for payment status (OOP)
│
├── .gitignore                           # Git ignore rules
└── README.md                            # Project documentation
```

---

## Installation & Setup

### Prerequisites

1. **Python 3.8 or higher**

   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure "Add Python to PATH" is checked during installation

2. **XAMPP**
   - Download from [apachefriends.org](https://www.apachefriends.org/)
   - Install and start MySQL service

### Step 1: Clone or Download Project

```bash
# Clone repository (if using Git)
git clone https://github.com/yourusername/laundry-system.git
cd laundry-system

# Or download and extract ZIP file
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install required packages
pip install PyQt6 mysql-connector-python
```

### Step 3: Setup Database

1. **Start XAMPP** and ensure MySQL is running
2. **Open phpMyAdmin** (http://localhost/phpmyadmin)
3. **Import Database:**

   - Click "New" to create database named `db_laundry`
   - Select `db_laundry` database
   - Click "Import" tab
   - Choose file: `src/db/db_laundry.sql`
   - Click "Go" to import

4. **Verify Admin Account:**
   - Navigate to `admin` table
   - Ensure at least one admin record exists
   - Default credentials should be in the database

### Step 4: Run Application

```bash
# Navigate to project directory
cd LaundrySystem

# Run main application
python src/gui/main_window.py
```

---

## Usage Guide

### For Administrators

1. **Login:**

   - Launch application
   - Click "Admin Log In" button
   - Enter credentials (username: `labandera`, password: `labandera_admin`)

2. **Add New Order:**

   - Click "Add Order" button
   - Fill in customer information
   - Select services and quantities
   - Adjust prices if needed (within min-max range)
   - Enter payment details
   - Click "Add Order" to save

3. **Manage Orders:**

   - View all orders in the main table
   - Click on an order to view details in side panels
   - Update payment status from dropdown
   - Update order status through workflow
   - Delete orders using "Delete Order" button

4. **Payment Management:**

   - Edit amount paid directly in the detail panel
   - System auto-determines payment status (Pending/Partial/Paid)
   - Payment status can be manually adjusted if needed
   - Completed payments automatically update order status

5. **Order Status Workflow:**
   - Pending Payment → Queueing (auto when paid)
   - Queueing → Washing/Cleaning
   - Washing/Cleaning → Finishing Up
   - Finishing Up → Ready for Pickup/Delivery
   - Ready for Pickup/Delivery → Completed
   - Any status → Cancelled (triggers auto-refund)

### For Customers

1. **Track Order:**

   - Enter Order ID in search box on main page
   - Click search button
   - View order status and details

2. **View Services:**
   - Click "Services" button
   - Browse available services by category
   - View pricing ranges

---

## Business Rules & Validation

### Payment Validation

- Amount paid cannot be negative
- "Paid" status requires full payment
- Partial payment automatically sets "Partial" status
- Zero payment sets "Pending" status

### Order Status Rules

- Orders cannot progress without payment started
- "Completed" requires full payment
- "Cancelled" triggers automatic refund
- Status transitions follow logical workflow

### Order Item Validation

- At least one service must be selected
- Quantities must be positive
- Prices must be within service min-max range

### Customer Validation

- Name and contact number are required
- Email format validation (if provided)

---

## Features Highlight

### Automatic Business Logic

- **Auto Payment Status**: System determines status based on amount paid
- **Auto Order Status**: Payment completion triggers order status update
- **Auto Refund**: Cancellation automatically sets payment to ₱0 and "Refunded"
- **Auto Date Tracking**: Payment date recorded when fully paid

### Data Integrity

- **Cascading Deletes**: Deleting order removes items and payments
- **Customer Cleanup**: Customers deleted when no orders remain
- **Referential Integrity**: Foreign keys maintain data consistency

### User Experience

- **Confirmation Dialogs**: Critical actions require confirmation
- **Real-time Updates**: Changes reflect immediately in interface
- **Visual Feedback**: Status-based colors and formatting
- **Input Validation**: Prevents invalid data entry

---

## Known Limitations

1. **Password Security**: Passwords stored in plain text (academic project)
2. **Single Admin Session**: No multi-user concurrent access handling
3. **No Backup Feature**: Manual database backup required
4. **Local Database**: Requires local MySQL server

---

## Future Enhancements

- Password hashing for security
- SMS/Email notifications for order status
- Reporting and analytics dashboard
- Inventory management integration
- Mobile application for customers
- Cloud database support
- Multi-branch management

---

## Credits & References

- **PyQt6 Documentation**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **MySQL Documentation**: https://dev.mysql.com/doc/
- **Python MySQL Connector**: https://dev.mysql.com/doc/connector-python/

---

## License

This project is developed for academic purposes as part of IT5 course requirement.

---

## Author

**Arianne Danielle V. Añora**  
BS Information Technology
University of Mindanao  
Date: October 2025

_Last Updated: October 15, 2025_
