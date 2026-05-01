"""Shared FastAPI dependencies for authentication and authorization.

All microservices import these to avoid duplication.
"""
from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from common.database import get_db
from common.security import get_security
from common.models import User
from common.repositories import UserRepository
from common.exceptions import UnauthorizedException, ForbiddenException


async def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Extract Bearer token from Authorization header."""
    if not authorization:
        raise UnauthorizedException("Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise UnauthorizedException("Invalid authorization scheme, use Bearer")
    return token


async def get_current_user(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db),
) -> User:
    """Dependency: extract and validate current user from JWT."""
    security = get_security()
    payload = security.decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload.get("user_id")
    repo = UserRepository(db)
    user = repo.get(user_id)
    if user is None:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("Account is deactivated")
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency: ensure current user has admin role."""
    if current_user.role != "admin":
        raise ForbiddenException("Admin access required")
    return current_user


async def get_manager_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency: ensure current user is at least manager."""
    if current_user.role not in ("admin", "manager"):
        raise ForbiddenException("Manager or admin access required")
    return current_user
