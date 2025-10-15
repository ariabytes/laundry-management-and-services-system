from decimal import Decimal
from datetime import datetime


class OrderValidator:

    def __init__(self):
        self.errors = []

    def validate_customer_info(self, name, phone, email, address):
        self.errors = []

        if not name or not name.strip():
            self.errors.append("Customer name is required")

        if not phone or not phone.strip():
            self.errors.append("Contact number is required")

        if email and '@' not in email:
            self.errors.append("Invalid email format")

        return len(self.errors) == 0

    def validate_order_items(self, items):
        self.errors = []

        if not items or len(items) == 0:
            self.errors.append("At least one service must be selected")
            return False

        for item in items:
            if item.get('qty', 0) <= 0:
                self.errors.append(
                    f"Invalid quantity for {item.get('service_name', 'service')}"
                )

            if item.get('price', 0) <= 0:
                self.errors.append(
                    f"Invalid price for {item.get('service_name', 'service')}"
                )

        return len(self.errors) == 0

    def validate_payment(self, amount_paid, total_price, payment_status):
        self.errors = []

        if amount_paid < 0:
            self.errors.append("Amount paid cannot be negative")

        if payment_status.lower() == "paid" and amount_paid < total_price:
            self.errors.append("Amount paid is less than total price")

        return len(self.errors) == 0

    def get_errors(self):
        return self.errors

    def get_error_message(self):
        if not self.errors:
            return ""
        return "\n".join(f"• {error}" for error in self.errors)


class PaymentProcessor:

    @staticmethod
    def calculate_total(order_items):
        total = Decimal("0.00")
        for item in order_items:
            qty = item.get("qty", 0)
            price = Decimal(str(item.get("price", 0)))
            total += qty * price
        return total

    @staticmethod
    def determine_payment_date(payment_status):
        status = payment_status.lower().strip()
        if status == "paid":
            return datetime.now()
        return None

    @staticmethod
    def determine_amount_paid(payment_status, total_price, custom_amount=None):
        status = payment_status.lower().strip()

        if status == "paid":
            return Decimal(str(total_price))
        elif status == "refunded":
            return Decimal("0")
        elif custom_amount is not None:
            return Decimal(str(custom_amount))
        else:
            return Decimal("0")

    @staticmethod
    def can_refund(payment_status):
        status = payment_status.lower().strip()
        return status in ["paid", "partial"]

    @staticmethod
    def should_auto_update_status(current_status, payment_status):
        if payment_status.lower() == "paid" and current_status.lower() == "pending payment":
            return True
        return False

    @staticmethod
    def determine_payment_status_from_amount(amount_paid, total_price):
        """
        Automatically determine payment status based on amount
        """
        amount_paid = Decimal(str(amount_paid))
        total_price = Decimal(str(total_price))

        if amount_paid <= 0:
            return "Pending"
        elif amount_paid >= total_price:
            return "Paid"
        else:
            return "Partial"


class OrderStatusManager:
    """
    Manages valid order status transitions and ensures they are consistent
    with payment and process logic.
    """

    VALID_TRANSITIONS = {
        "pending payment": ["queueing", "cancelled"],
        "queueing": ["washing/cleaning", "cancelled"],
        "washing/cleaning": ["finishing up", "cancelled"],
        "finishing up": ["ready for pickup/delivery!", "cancelled"],
        "ready for pickup/delivery!": ["completed", "cancelled"],
        "completed": [],
        "cancelled": []
    }

    @classmethod
    def can_transition(cls, from_status, to_status):
        from_status = from_status.lower().strip()
        to_status = to_status.lower().strip()

        valid_next = cls.VALID_TRANSITIONS.get(from_status, [])
        return to_status in valid_next

    @classmethod
    def get_next_status(cls, current_status):
        current_status = current_status.lower().strip()
        return cls.VALID_TRANSITIONS.get(current_status, [])

    @staticmethod
    def should_refund_on_cancel(order_status, payment_status):
        return (
            order_status.lower() == "cancelled"
            and payment_status.lower() in ["paid", "partial"]
        )

    @classmethod
    def validate_status_with_payment(cls, new_order_status, payment_status, amount_paid, total_price):
        """
        Validates if the new order status makes sense based on payment.
        """
        new_order_status = new_order_status.lower().strip()
        payment_status = payment_status.lower().strip()

        amount_paid = Decimal(str(amount_paid))
        total_price = Decimal(str(total_price))

        # Rule 1: Cannot complete unless fully paid
        if new_order_status == "completed":
            if payment_status != "paid":
                return False, "Order cannot be completed unless payment status is 'Paid'."
            if amount_paid < total_price:
                return False, f"Order cannot be completed. Amount paid (₱{float(amount_paid):.2f}) is less than total (₱{float(total_price):.2f})."

        # Rule 2: Cannot start process (Queueing or later) without payment started
        if new_order_status in [
            "queueing",
            "washing/cleaning",
            "finishing up",
            "ready for pickup/delivery!"
        ]:
            if payment_status in ["pending", "unpaid"] or amount_paid <= 0:
                return False, f"Order cannot move to '{new_order_status.title()}' without any payment."

        return True, ""

    @classmethod
    def validate_transition_with_payment(cls, from_status, to_status, payment_status, amount_paid, total_price):
        """
        Comprehensive validation for transitions considering process and payment.
        """
        # 1️⃣ Check logical process flow
        if not cls.can_transition(from_status, to_status):
            valid_next = cls.get_next_status(from_status)
            if valid_next:
                return (
                    False,
                    f"Invalid transition from '{from_status.title()}' to '{to_status.title()}'. "
                    f"Valid next statuses: {', '.join([s.title() for s in valid_next])}."
                )
            else:
                return False, f"'{from_status.title()}' is a final status and cannot be changed."

        # 2️⃣ Check payment consistency
        return cls.validate_status_with_payment(to_status, payment_status, amount_paid, total_price)


class PaymentStatusValidator:
    """
    Validates payment status changes and determines correct status.
    """

    @staticmethod
    def validate_payment_status_change(new_payment_status, amount_paid, total_price):
        """
        Validate if payment status change is appropriate.
        Returns: (is_valid, error_message, suggested_status)
        """
        new_payment_status = new_payment_status.lower().strip()
        amount_paid = Decimal(str(amount_paid))
        total_price = Decimal(str(total_price))

        # Determine what status SHOULD be based on amount
        if amount_paid <= 0:
            correct_status = "pending"
        elif amount_paid >= total_price:
            correct_status = "paid"
        else:
            correct_status = "partial"

        # Special cases that are always allowed
        if new_payment_status in ["refunded", "cancelled"]:
            return True, "", new_payment_status

        # Check if chosen status matches the amount
        if new_payment_status == "paid" and amount_paid < total_price:
            return (
                False,
                f"Cannot set status to 'Paid' when amount paid (₱{float(amount_paid):.2f}) is less than total (₱{float(total_price):.2f}).",
                correct_status,
            )

        if new_payment_status in ["pending", "unpaid"] and amount_paid > 0:
            return (
                False,
                f"Cannot set status to '{new_payment_status.title()}' when amount paid is ₱{float(amount_paid):.2f}. Use 'Partial' instead.",
                correct_status,
            )

        if new_payment_status == "partial" and (amount_paid <= 0 or amount_paid >= total_price):
            if amount_paid <= 0:
                return (
                    False,
                    "Cannot set status to 'Partial' when no payment has been made. Use 'Pending' instead.",
                    correct_status,
                )
            else:
                return (
                    False,
                    "Cannot set status to 'Partial' when full amount is paid. Use 'Paid' instead.",
                    correct_status,
                )

        return True, "", new_payment_status

    @staticmethod
    def auto_determine_payment_status(amount_paid, total_price):
        """
        Automatically determine the correct payment status based on amount.
        Returns: status name as string.
        """
        amount_paid = Decimal(str(amount_paid))
        total_price = Decimal(str(total_price))

        if amount_paid <= 0:
            return "Pending"
        elif amount_paid >= total_price:
            return "Paid"
        else:
            return "Partial"
