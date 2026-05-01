"""Domain-specific repositories extending BaseRepository."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from common.repositories.base import BaseRepository
from common.models import (
    User, Employee, Attendance, LeaveBalance, Leave,
    ShiftTemplate, Shift, ShiftAssignment,
    Receipt, ExpenseCategory, Expense, InventoryItem, Invoice,
)


# ─── AUTH ───────────────────────────────────────────────

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.get_by(email=email)


# ─── HR ─────────────────────────────────────────────────

class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, db: Session):
        super().__init__(Employee, db)

    def get_active(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        return self.list(skip=skip, limit=limit, is_active=True)

    def get_by_department(self, department: str) -> List[Employee]:
        return self.list(department=department, is_active=True)

    def create_from_schema(self, schema, exclude_unset: bool = False) -> Employee:
        """Create employee, optionally creating a linked User account."""
        data = schema.model_dump(exclude_unset=exclude_unset)
        # Extract user-creation fields (not part of Employee model)
        password = data.pop("password", None)
        user_id = data.pop("user_id", None)
        # Create Employee
        employee = self.create(**data)
        # If password provided, create a User account for login
        if password and employee.email:
            try:
                from common.models import User
                from common.security import get_security
                from common.repositories import UserRepository
                security = get_security()
                hashed = security.hash_password(password)
                user_repo = UserRepository(self.db)
                user_repo.create(
                    email=employee.email,
                    hashed_password=hashed,
                    full_name=employee.name,
                    role="employee",
                    is_active=True,
                )
            except Exception:
                pass  # User creation is optional
        return employee


class AttendanceRepository(BaseRepository[Attendance]):
    def __init__(self, db: Session):
        super().__init__(Attendance, db)

    def get_by_employee_and_date(self, employee_id: int, date: str) -> Optional[Attendance]:
        return self.get_by(employee_id=employee_id, date=date)

    def get_today_attendance(self, date: str) -> List[Attendance]:
        return self.list(date=date)

    def get_employee_history(self, employee_id: int, limit: int = 30) -> List[Attendance]:
        return self.list(employee_id=employee_id, order_by="date", descending=True, limit=limit)


class LeaveBalanceRepository(BaseRepository[LeaveBalance]):
    def __init__(self, db: Session):
        super().__init__(LeaveBalance, db)

    def get_employee_balance(self, employee_id: int, year: int) -> List[LeaveBalance]:
        return self.list(employee_id=employee_id, year=year)


class LeaveRepository(BaseRepository[Leave]):
    def __init__(self, db: Session):
        super().__init__(Leave, db)

    def get_pending(self) -> List[Leave]:
        return self.list(status="pending")

    def get_by_employee(self, employee_id: int) -> List[Leave]:
        return self.list(employee_id=employee_id, order_by="created_at", descending=True)


class ShiftTemplateRepository(BaseRepository[ShiftTemplate]):
    def __init__(self, db: Session):
        super().__init__(ShiftTemplate, db)

    def get_by_day(self, day_of_week: int) -> List[ShiftTemplate]:
        return self.list(day_of_week=day_of_week, is_active=True)


class ShiftRepository(BaseRepository[Shift]):
    def __init__(self, db: Session):
        super().__init__(Shift, db)

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Shift]:
        return self.db.query(Shift).filter(
            Shift.date >= start_date, Shift.date <= end_date
        ).all()


class ShiftAssignmentRepository(BaseRepository[ShiftAssignment]):
    def __init__(self, db: Session):
        super().__init__(ShiftAssignment, db)

    def get_by_shift(self, shift_id: int) -> List[ShiftAssignment]:
        return self.list(shift_id=shift_id)

    def get_by_employee(self, employee_id: int) -> List[ShiftAssignment]:
        return self.list(employee_id=employee_id)


# ─── FINANCE ────────────────────────────────────────────

class ReceiptRepository(BaseRepository[Receipt]):
    def __init__(self, db: Session):
        super().__init__(Receipt, db)


class ExpenseCategoryRepository(BaseRepository[ExpenseCategory]):
    def __init__(self, db: Session):
        super().__init__(ExpenseCategory, db)

    def get_active(self) -> List[ExpenseCategory]:
        return self.list(is_active=True)


class ExpenseRepository(BaseRepository[Expense]):
    def __init__(self, db: Session):
        super().__init__(Expense, db)

    def get_summary(self, start_date: str = "", end_date: str = "") -> Dict[str, Any]:
        """Get expense summary with totals and category breakdown."""
        query = self.db.query(
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        )
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)
        result = query.first()

        # Category breakdown
        cat_query = self.db.query(
            Expense.category,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        )
        if start_date:
            cat_query = cat_query.filter(Expense.date >= start_date)
        if end_date:
            cat_query = cat_query.filter(Expense.date <= end_date)
        cat_query = cat_query.group_by(Expense.category)
        categories = {row.category: {"total": float(row.total), "count": row.count} for row in cat_query.all()}

        total = float(result.total or 0)
        count = result.count or 0
        return {
            "total": total,
            "count": count,
            "by_category": categories,
            "average": round(total / count, 2) if count > 0 else 0,
        }

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Expense]:
        return self.db.query(Expense).filter(
            Expense.date >= start_date, Expense.date <= end_date
        ).order_by(Expense.date.desc()).all()


class InventoryRepository(BaseRepository[InventoryItem]):
    def __init__(self, db: Session):
        super().__init__(InventoryItem, db)

    def get_low_stock(self) -> List[InventoryItem]:
        return self.db.query(InventoryItem).filter(
            InventoryItem.quantity <= InventoryItem.min_stock
        ).all()

    def get_by_category(self, category: str) -> List[InventoryItem]:
        return self.list(category=category)


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, db: Session):
        super().__init__(Invoice, db)

    def get_by_status(self, status: str) -> List[Invoice]:
        return self.list(status=status)
