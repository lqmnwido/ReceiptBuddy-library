"""ReceiptBuddy Common — Shared library for all microservices.

Provides base models, schemas, repositories, security, and database management
that all microservices import to avoid code duplication.
"""
from common.config import ServiceSettings
from common.database import DatabaseManager, get_database, get_db
from common.security import SecurityManager, get_security
