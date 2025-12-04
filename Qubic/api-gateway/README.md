# API Gateway Service

FastAPI gateway service providing REST endpoints for task management and audit access.

## Endpoints

- `POST /task/start` - Start a new task
- `GET /task/{id}` - Get task status
- `POST /task/{id}/approve` - Approve/reject a task
- `GET /audit/{task_id}` - Get audit log for a task
- `GET /health` - Health check

## Environment Variables

- `PORT` - Service port (default: 8000)
- `REDIS_URL` - Redis connection URL
- `PLANNER_SERVICE_URL` - Planner service URL
- `AGENT_RUNTIME_URL` - Agent runtime service URL
- `AUDIT_SERVICE_URL` - Audit service URL
- `LOG_LEVEL` - Logging level (default: INFO)

## Authentication

Currently uses a stub OAuth implementation. In production, implement JWT token validation in `verify_token()`.

## Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

