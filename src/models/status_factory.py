from datetime import datetime
from decimal import Decimal


class PaymentStatus:

    def __init__(self, status_name):
        self.status_name = status_name

    def get_payment_date(self):
        return None

    def get_amount_paid(self, total_price):
        return Decimal("0")

    def can_modify_amount(self):
        return True

    def get_display_color(self):
        return "#333333"


class PendingStatus(PaymentStatus):

    def __init__(self):
        super().__init__("Pending")

    def get_display_color(self):
        return "#ffc107"


class PartialStatus(PaymentStatus):

    def __init__(self):
        super().__init__("Partial")

    def get_amount_paid(self, total_price):
        return Decimal("0")

    def get_display_color(self):
        return "#fd7e14"


class PaidStatus(PaymentStatus):

    def __init__(self):
        super().__init__("Paid")

    def get_payment_date(self):
        return datetime.now()

    def get_amount_paid(self, total_price):
        return Decimal(str(total_price))

    def can_modify_amount(self):
        return False

    def get_display_color(self):
        return "#28a745"


class FailedStatus(PaymentStatus):

    def __init__(self):
        super().__init__("Failed")

    def get_display_color(self):
        return "#dc3545"


class RefundedStatus(PaymentStatus):

    def __init__(self):
        super().__init__("Refunded")

    def get_amount_paid(self, total_price):
        return Decimal("0")

    def can_modify_amount(self):
        return False

    def get_display_color(self):
        return "#6c757d"


class PaymentStatusFactory:

    _status_map = {
        "pending": PendingStatus,
        "partial": PartialStatus,
        "paid": PaidStatus,
        "failed": FailedStatus,
        "refunded": RefundedStatus,
    }

    @classmethod
    def create(cls, status_name):
        status_key = status_name.lower().strip()
        status_class = cls._status_map.get(status_key)
        if status_class:
            return status_class()
        return PaymentStatus(status_name)

    @classmethod
    def get_all_statuses(cls):
        return list(cls._status_map.keys())
