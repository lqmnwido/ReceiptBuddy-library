"""All SQLAlchemy domain models organized by business domain.

Domains:
  - Auth: User
  - HR: Employee, Attendance, LeaveBalance, Leave, ShiftTemplate, Shift, ShiftAssignment
  - Finance: Receipt, ExpenseCategory, Expense, InventoryItem, Invoice
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from common.models.base import Base, TimestampedBase, SoftDeleteMixin


# ──────────────────────────────────────────────
# AUTH DOMAIN
# ──────────────────────────────────────────────

class User(TimestampedBase):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="employee")  # admin, manager, employee
    is_active = Column(Boolean, default=True)

    # Relationships
    employees = relationship("Employee", back_populates="user")


# ──────────────────────────────────────────────
# HR DOMAIN
# ──────────────────────────────────────────────

class Employee(TimestampedBase):
    __tablename__ = "employees"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    hourly_rate = Column(Float, default=15.0)
    max_hours_per_week = Column(Integer, default=40)
    min_hours_per_week = Column(Integer, default=0)
    preferred_shifts = Column(JSON, default=[])  # ['morning', 'evening', 'night']
    unavailable_dates = Column(JSON, default=[])
    skills = Column(JSON, default=[])
    profile_image = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="employees")
    attendance_records = relationship("Attendance", back_populates="employee")
    leave_balances = relationship("LeaveBalance", back_populates="employee")
    leave_requests = relationship("Leave", back_populates="employee")
    shifts = relationship("ShiftAssignment", back_populates="employee")
    expenses = relationship("Expense", back_populates="employee")


class Attendance(TimestampedBase):
    __tablename__ = "attendance"

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    clock_in = Column(DateTime, nullable=True)
    clock_out = Column(DateTime, nullable=True)
    clock_in_lat = Column(Float, nullable=True)
    clock_in_lng = Column(Float, nullable=True)
    clock_out_lat = Column(Float, nullable=True)
    clock_out_lng = Column(Float, nullable=True)
    hours_worked = Column(Float, nullable=True)
    is_late = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    employee = relationship("Employee", back_populates="attendance_records")


class LeaveBalance(TimestampedBase):
    __tablename__ = "leave_balances"

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(String(50), nullable=False)  # annual, sick, medical, unpaid
    total_days = Column(Integer, default=0)
    used_days = Column(Integer, default=0)
    year = Column(Integer, nullable=False)

    employee = relationship("Employee", back_populates="leave_balances")


class Leave(TimestampedBase):
    __tablename__ = "leaves"

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=False)
    days_requested = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="pending", index=True)  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    employee = relationship("Employee", back_populates="leave_requests")


class ShiftTemplate(TimestampedBase):
    __tablename__ = "shift_templates"

    name = Column(String(100), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(String(5), nullable=False)  # HH:MM
    end_time = Column(String(5), nullable=False)
    role_needed = Column(String(100), nullable=True)
    min_staff = Column(Integer, default=1)
    preferred_skills = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)


class Shift(TimestampedBase):
    __tablename__ = "shifts"

    date = Column(String(10), nullable=False, index=True)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    role_needed = Column(String(100), nullable=True)
    min_staff = Column(Integer, default=1)
    preferred_skills = Column(JSON, default=[])

    assignments = relationship("ShiftAssignment", back_populates="shift")


class ShiftAssignment(TimestampedBase):
    __tablename__ = "shift_assignments"

    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    assigned_at = Column(DateTime, server_default=func.now())

    shift = relationship("Shift", back_populates="assignments")
    employee = relationship("Employee", back_populates="shifts")


# ──────────────────────────────────────────────
# FINANCE DOMAIN
# ──────────────────────────────────────────────

class Receipt(TimestampedBase):
    __tablename__ = "receipts"

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    filename = Column(String(500), nullable=False)
    image_url = Column(String(500), nullable=True)
    vendor = Column(String(255), nullable=True)
    total = Column(Float, nullable=True)
    date = Column(String(10), nullable=True)
    category = Column(String(100), nullable=True)
    raw_text = Column(Text, nullable=True)
    line_items = Column(JSON, default=[])
    confidence = Column(Float, default=0.0)

    expense = relationship("Expense", back_populates="receipt", uselist=False)


class ExpenseCategory(TimestampedBase):
    __tablename__ = "expense_categories"

    name = Column(String(100), unique=True, nullable=False)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)
    is_active = Column(Boolean, default=True)

    # Note: No relationship to Expense here because Expense uses a string
    # category field, not a foreign key. Query by category name instead.


class Expense(TimestampedBase):
    __tablename__ = "expenses"

    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    category = Column(String(100), nullable=True)
    amount = Column(Float, nullable=False)
    description = Column(String(500), nullable=True)
    date = Column(String(10), nullable=False, index=True)
    is_recurring = Column(Boolean, default=False)
    recurring_interval = Column(String(20), nullable=True)

    receipt = relationship("Receipt", back_populates="expense")
    employee = relationship("Employee", back_populates="expenses")


class InventoryItem(TimestampedBase):
    __tablename__ = "inventory"

    name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True, nullable=True)
    category = Column(String(100), nullable=True)
    quantity = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    unit_price = Column(Float, nullable=True)
    supplier = Column(String(255), nullable=True)


class Invoice(TimestampedBase):
    __tablename__ = "invoices"

    invoice_number = Column(String(50), unique=True, nullable=False)
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), nullable=True)
    client_address = Column(Text, nullable=True)
    items = Column(JSON, default=[])
    subtotal = Column(Float, default=0)
    tax_rate = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    total = Column(Float, default=0)
    status = Column(String(20), default="draft", index=True)  # draft, sent, paid, overdue
    due_date = Column(String(10), nullable=True)
    paid_date = Column(String(10), nullable=True)
    notes = Column(Text, nullable=True)
