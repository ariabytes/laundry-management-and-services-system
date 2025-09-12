# Laundry Monitoring and Services System

## Introduction

The **Laundry Monitoring and Services System** is a Python application (desktop GUI or web) with a MySQL (XAMPP) backend. It streamlines laundry shop operations by enabling administrators to manage orders efficiently and allowing clients to conveniently track their laundry status using a unique Order ID.

---

## Problem Statement

Local laundry shops often rely on manual, paper-based processes for managing orders, receipts, and payments. This results in misplaced orders, inaccurate time estimates, billing errors, and inefficient record-keeping for both business owners and clients.

---

## Target Users

- Laundry shop owners and staff
- Laundry shop clients
- Individuals inquiring about laundry services

---

## Features

- **Automated Order Management:** Staff can digitally record orders, services, and payments.
- **Real-Time Tracking:** Clients can check laundry status and bill instantly by entering their Order ID.
- **Efficient Workflows:** Reduces repetitive staff tasks and manual inquiries.
- **Accurate Billing:** Automated calculations minimize human error.
- **Organized Records:** All data is securely stored in MySQL, enabling search, update, and reporting.

---

## Database Overview

**Entities:**

- `admins`: Admin/staff login credentials and info
- `customers`: Customer details
- `orders`: Orders placed, linked to customers
- `order_items`: Services/add-ons per order
- `payments`: Payment records per order
- `categories`: Service categories
- `services`: Service items and add-ons
- `order_statuses`: Progress tracking for orders
- `payment_statuses`: Status of payments
- `payment_methods`: Modes of payment

**Entity Relationships Diagram:**

```
[admins]
   |
   v
[customers]----< [orders] >----[order_statuses]
       |                        |
       |                        v
       |                  [order_items] >----[services]----[categories]
       |                                                      ^
       |                                                      |
       |                                             [payments]----[payment_statuses]
       |                                                      |
       |                                                      v
       |                                      [payment_methods]
```

---

## Technologies Used

- **Python** (GUI: Tkinter, PyQt, or similar)
- **MySQL** (via XAMPP)
- **SQLAlchemy** (optional, for ORM)
- **VS Code** or any Python IDE

---

## Conceptual Project Structure (Initial)

```
LaundryMonitoringSystem/
│
├── db/          # Database connection and helpers
├── models/      # Data classes for entities
├── gui/         # GUI classes/windows
├── utils/       # Helper functions
├── app.py       # Main entry point
├── .gitignore
└── README.md
```

---

## Getting Started

1. **Clone the repository**
2. **Set up MySQL database** (see `/db/connection.py` for details)
3. **Update database credentials** in your config
4. **Run `app.py`** to start the application

---

## Future Plans

- Connect db to the backend
- Add full CRUD operations for all entities
- Implement GUI screens for staff and clients
- Add reporting and analytics features

---

## Author

Arianne Danielle V. Añora
