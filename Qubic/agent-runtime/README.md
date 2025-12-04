# Agent Runtime Service

Nostramos-style multi-agent orchestration runtime that manages plan execution and agent coordination.

## Architecture

The service implements a simplified Nostramos-style agent registry with four agent types:

1. **planner_agent** - Validates plan structure
2. **execution_agent** - Dispatches tasks to worker service
3. **audit_agent** - Records execution in audit service
4. **compliance_agent** - Checks compliance rules and approvals

## Endpoints

- `POST /plan/execute` - Execute a plan
- `GET /task/{task_id}/status` - Get task execution status
- `POST /task/{task_id}/approve` - Process approval for a task
- `GET /health` - Health check

## Agent Dispatch Flow

1. Plan received → Steps executed sequentially
2. For each step:
   - Compliance check (approval required?)
   - Execution dispatch to worker
   - Audit recording
3. Status tracked in Redis

## Environment Variables

- `PORT` - Service port (default: 8000)
- `REDIS_URL` - Redis connection URL
- `WORKER_SERVICE_URL` - Worker service URL
- `AUDIT_SERVICE_URL` - Audit service URL
- `LOG_LEVEL` - Logging level (default: INFO)

## Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

