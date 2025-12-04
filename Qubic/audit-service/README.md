# Audit Service

Audit logging service with PostgreSQL persistence and Qubic blockchain integration.

## Features

- SHA-256 hashing of all inputs/outputs
- PostgreSQL storage with Alembic migrations
- Qubic blockchain integration (with retry logic)
- Hash verification endpoints

## Database Schema

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR NOT NULL,
    step_index INTEGER,
    step_type VARCHAR,
    input_hash VARCHAR,
    output_hash VARCHAR,
    status VARCHAR,
    timestamp TIMESTAMP,
    qubic_txid VARCHAR,
    metadata TEXT
);
```

## Endpoints

- `POST /audit/record` - Record an audit log entry
- `GET /audit/{task_id}` - Get audit log for a task
- `GET /audit/verify/{hash}` - Verify hash in Qubic
- `GET /health` - Health check

## Environment Variables

- `PORT` - Service port (default: 8000)
- `DATABASE_URL` - PostgreSQL connection URL
- `QUBIC_SERVICE_URL` - Qubic service URL
- `MINIO_ENDPOINT` - MinIO endpoint
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key
- `LOG_LEVEL` - Logging level (default: INFO)

## Database Migrations

Run migrations:

```bash
alembic upgrade head
```

Create new migration:

```bash
alembic revision --autogenerate -m "description"
```

## Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

