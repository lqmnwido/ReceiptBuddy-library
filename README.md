# ReceiptBuddy Library

Shared Python library for all ReceiptBuddy microservices.

## What's Inside

| Module | Description |
|--------|-------------|
| `common.config` | `ServiceSettings` — Pydantic-based settings with env var support |
| `common.database` | SQLAlchemy engine, session factory, `Base`, `init_db()` |
| `common.models` | All SQLAlchemy ORM models (User, Employee, Expense, Receipt, etc.) |
| `common.schemas` | Pydantic request/response schemas for all services |
| `common.repositories` | `BaseRepository[T]` with generic CRUD + domain-specific repos |
| `common.security` | JWT creation/verification, password hashing |
| `common.dependencies` | FastAPI `Depends()` helpers (`get_current_user`, `get_admin_user`) |
| `common.exceptions` | Exception hierarchy (`NotFoundException`, `ConflictException`, etc.) |
| `common.services.storage` | MinIO/S3 file storage abstraction |

## Usage

```python
# In any microservice
from common.config import ServiceSettings
from common.database import get_db
from common.repositories import ExpenseRepository
from common.schemas import ExpenseResponse
from common.dependencies import get_current_user
```

## Install

As a pip dependency from GitHub:

```txt
receiptbuddy-common @ git+https://github.com/lqmnwido/ReceiptBuddy-library.git
```

Or locally for development:

```bash
pip install -e ./common
```

## Environment Variables

See `common/config.py` for all settings. Key ones:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `SECRET_KEY` | — | JWT signing secret |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection |
| `MINIO_ENDPOINT` | `localhost:9000` | S3-compatible storage |
| `OLLAMA_URL` | `http://localhost:11434` | LLM inference endpoint |

## Publishing

To publish a new version:

```bash
# Bump version in pyproject.toml
git tag v1.0.1
git push origin v1.0.1
```

Submodules reference this library via `@ git+https://github.com/lqmnwido/ReceiptBuddy-library.git` in their `requirements.txt`, so updates are picked up on rebuild.
