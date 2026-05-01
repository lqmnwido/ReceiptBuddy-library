"""JWT and password security — shared across all services."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Handles JWT tokens and password hashing for all services."""

    def __init__(self, secret_key: str, algorithm: str = "HS256", expire_minutes: int = 1440):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    # --- Password hashing ---
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    # --- JWT tokens ---
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return None

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        payload = self.decode_access_token(token)
        if payload is None:
            return None
        return payload.get("user_id")

    def get_role_from_token(self, token: str) -> Optional[str]:
        payload = self.decode_access_token(token)
        if payload is None:
            return None
        return payload.get("role")


# Default instance (lazy)
_default_security: SecurityManager = None


def get_security() -> SecurityManager:
    global _default_security
    if _default_security is None:
        from common.config import ServiceSettings
        settings = ServiceSettings()
        _default_security = SecurityManager(settings.SECRET_KEY, settings.ALGORITHM, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _default_security
