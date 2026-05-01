"""Shared Pydantic schemas — common + domain models."""
from datetime import datetime
from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


# ─── PAGINATION ───────────────────────────────────

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int = 1
    page_size: int = 100
    pages: int = 1


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(100, ge=1, le=500)
    sort_by: Optional[str] = None
    sort_desc: bool = False


# ─── COMMON ───────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = ""
    version: str = "1.0.0"
    database: str = "connected"


class ErrorResponse(BaseModel):
    error: str
    type: str
    details: Optional[Dict[str, Any]] = None


# ─── AUTH SCHEMAS ─────────────────────────────────

class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "employee"


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


# ─── HR SCHEMAS ───────────────────────────────────

class EmployeeBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    hourly_rate: float = 15.0
    max_hours_per_week: int = 40
    min_hours_per_week: int = 0
    preferred_shifts: List[str] = []
    unavailable_dates: List[str] = []
    skills: List[str] = []


class EmployeeCreate(EmployeeBase):
    password: Optional[str] = None
    user_id: Optional[int] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    hourly_rate: Optional[float] = None
    max_hours_per_week: Optional[int] = None
    min_hours_per_week: Optional[int] = None
    preferred_shifts: Optional[List[str]] = None
    unavailable_dates: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: int
    user_id: Optional[int]
    profile_image: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceBase(BaseModel):
    employee_id: int
    date: str


class AttendanceClockIn(AttendanceBase):
    lat: Optional[float] = None
    lng: Optional[float] = None


class AttendanceClockOut(AttendanceBase):
    lat: Optional[float] = None
    lng: Optional[float] = None


class AttendanceResponse(AttendanceBase):
    id: int
    clock_in: Optional[datetime]
    clock_out: Optional[datetime]
    hours_worked: Optional[float]
    is_late: bool
    clock_in_lat: Optional[float]
    clock_in_lng: Optional[float]
    clock_out_lat: Optional[float]
    clock_out_lng: Optional[float]

    class Config:
        from_attributes = True


class LeaveBalanceResponse(BaseModel):
    leave_type: str
    total_days: int
    used_days: int
    remaining: int

    class Config:
        from_attributes = True


class LeaveRequest(BaseModel):
    employee_id: int
    leave_type: str
    start_date: str
    end_date: str
    reason: Optional[str] = None


class LeaveUpdate(BaseModel):
    status: str  # approved, rejected
    rejection_reason: Optional[str] = None


class LeaveResponse(LeaveRequest):
    id: int
    days_requested: int
    status: str
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ShiftTemplateBase(BaseModel):
    name: str
    day_of_week: int
    start_time: str
    end_time: str
    role_needed: Optional[str] = None
    min_staff: int = 1
    preferred_skills: List[str] = []


class ShiftTemplateCreate(ShiftTemplateBase):
    pass


class ShiftTemplateResponse(ShiftTemplateBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class ShiftGenerateRequest(BaseModel):
    start_date: str
    end_date: str


class ShiftAssignmentResponse(BaseModel):
    shift_id: int
    employee_id: int
    employee_name: Optional[str] = None
    date: str
    start_time: str
    end_time: str

    class Config:
        from_attributes = True


# ─── FINANCE SCHEMAS ──────────────────────────────

class ReceiptUploadResponse(BaseModel):
    receipt_id: int
    vendor: Optional[str]
    total: Optional[float]
    category: Optional[str]
    date: Optional[str]
    confidence: float
    image_url: Optional[str]
    line_items: List[dict] = []


class ExpenseCreate(BaseModel):
    receipt_id: Optional[int] = None
    employee_id: Optional[int] = None
    category: str
    amount: float
    description: Optional[str] = None
    date: str
    is_recurring: bool = False
    recurring_interval: Optional[str] = None


class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_interval: Optional[str] = None


class ExpenseResponse(ExpenseCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseSummary(BaseModel):
    total: float
    count: int
    by_category: Dict[str, Any]
    average: float


class InventoryItemBase(BaseModel):
    name: str
    sku: Optional[str] = None
    category: Optional[str] = None
    quantity: int = 0
    min_stock: int = 0
    unit_price: Optional[float] = None
    supplier: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    min_stock: Optional[int] = None
    unit_price: Optional[float] = None
    supplier: Optional[str] = None


class InventoryItemResponse(InventoryItemBase):
    id: int
    needs_reorder: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    client_name: str
    client_email: Optional[str] = None
    client_address: Optional[str] = None
    items: List[dict] = []
    subtotal: float = 0
    tax_rate: float = 0
    tax_amount: float = 0
    total: float = 0
    due_date: Optional[str] = None
    notes: Optional[str] = None


class InvoiceResponse(InvoiceCreate):
    id: int
    invoice_number: str
    status: str
    paid_date: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsKPIs(BaseModel):
    total_expenses: float = 0
    total_payroll: float = 0
    avg_attendance_rate: float = 0
    labor_cost_percentage: float = 0
    top_expense_category: str = ""
    pending_leave_requests: int = 0
    low_stock_items: int = 0


class AIChatRequest(BaseModel):
    query: str


class AIChatResponse(BaseModel):
    answer: str
    context_used: bool = False
