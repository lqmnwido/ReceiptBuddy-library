"""Custom exception hierarchy for ReceiptBuddy."""
from typing import Optional, Any, Dict


class ReceiptBuddyException(Exception):
    """Base exception for all application errors."""
    status_code: int = 500
    message: str = "Internal server error"
    details: Optional[Dict[str, Any]] = None

    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class NotFoundException(ReceiptBuddyException):
    status_code = 404
    message = "Resource not found"


class ConflictException(ReceiptBuddyException):
    status_code = 409
    message = "Resource already exists"


class UnauthorizedException(ReceiptBuddyException):
    status_code = 401
    message = "Not authenticated"


class ForbiddenException(ReceiptBuddyException):
    status_code = 403
    message = "Not authorized"


class ValidationException(ReceiptBuddyException):
    status_code = 422
    message = "Validation error"


class ServiceUnavailableException(ReceiptBuddyException):
    status_code = 503
    message = "Service temporarily unavailable"


def as_json_response(exc: ReceiptBuddyException) -> Dict[str, Any]:
    """Convert an exception to a JSON-serializable dict for FastAPI responses."""
    return {
        "error": exc.message,
        "type": type(exc).__name__,
        "details": exc.details,
        "status_code": exc.status_code,
    }
