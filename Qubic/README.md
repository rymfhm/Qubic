# Qubic Autonomous Execution System

A production-quality prototype for an AI-driven autonomous execution system with blockchain-based auditing and governance.

## Architecture

The system consists of 8 microservices:

1. **api-gateway** - FastAPI gateway with OAuth-ready authentication and REST endpoints
2. **planner-service** - LangGraph-based task planning service
3. **agent-runtime** - Nostramos multi-agent orchestration runtime
4. **worker-service** - Task execution workers
5. **audit-service** - Audit logging with Qubic blockchain integration
6. **qubic-service** - Mock Qubic blockchain service
7. **postgres** - PostgreSQL database for persistence
8. **redis** - Redis for queues and locks
9. **minio** - S3-compatible object storage for artifacts

## Tech Stack

- Python 3.11+
- FastAPI for APIs
- LangGraph for task planning
- Nostramos for multi-agent orchestration
- Redis for queues/locks
- PostgreSQL for persistence
- MinIO (S3 compatible) for artifacts
- Docker + docker-compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)

### Start All Services

```bash
docker-compose up --build
```

This will start all services. Wait for all health checks to pass (about 30-60 seconds).

### Verify Services

Check health endpoints:

```bash
curl http://localhost:8000/health  # api-gateway
curl http://localhost:8001/health  # qubic-service
curl http://localhost:8002/health  # audit-service
curl http://localhost:8003/health  # worker-service
curl http://localhost:8004/health  # planner-service
curl http://localhost:8005/health  # agent-runtime
```

## Demo Workflow

### 1. Start a Task

```bash
curl -X POST http://localhost:8000/task/start \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "monitor_wallet",
    "wallet_address": "0x1234567890abcdef",
    "description": "Monitor wallet balance"
  }'
```

Response will include a `task_id`.

### 2. Check Task Status

```bash
curl http://localhost:8000/task/{task_id}
```

### 3. Approve Task (if required)

```bash
curl -X POST http://localhost:8000/task/{task_id}/approve \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "reason": "Approved for execution"
  }'
```

### 4. View Audit Log

```bash
curl http://localhost:8000/audit/{task_id}
```

## API Endpoints

### API Gateway (Port 8000)

- `POST /task/start` - Start a new task
- `GET /task/{id}` - Get task status
- `POST /task/{id}/approve` - Approve/reject task
- `GET /audit/{task_id}` - Get audit log for task
- `GET /health` - Health check

## Service Details

See individual README files in each service directory:
- `api-gateway/README.md`
- `planner-service/README.md`
- `agent-runtime/README.md`
- `worker-service/README.md`
- `audit-service/README.md`
- `qubic-service/README.md`

## Development

### Local Development

Each service can be run locally:

```bash
cd api-gateway
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Environment Variables

Each service uses environment variables for configuration. See individual service READMEs for details.

## Testing

Run the demo script:

```bash
./scripts/demo.sh
```

Or use the provided curl examples in `scripts/` directory.

## Database Migrations

Database migrations are managed with Alembic. To run migrations:

```bash
cd audit-service
alembic upgrade head
```

## Security Notes

- Never store secrets in code
- All secrets use environment variables
- Inputs/outputs are hashed before Qubic writes
- PII is not stored in database
- High-risk actions require approval
- Qubic is authoritative for policy decisions

## License

MIT

