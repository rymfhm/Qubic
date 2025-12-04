# Planner Service

LangGraph-based task planning service that converts user tasks into structured execution plans.

## Architecture

The service implements a simplified LangGraph workflow with three nodes:

1. **analyze_task** - Analyzes the task and determines requirements
2. **policy_check** - Checks policies with Qubic service
3. **plan_builder** - Builds structured execution steps

## Endpoints

- `POST /plan/create` - Create a new execution plan
- `GET /plan/{plan_id}` - Get plan details
- `GET /health` - Health check

## Plan Structure

Plans are returned as JSON with the following structure:

```json
{
  "plan_id": "...",
  "task_id": "...",
  "steps": [
    {
      "step_id": "1",
      "type": "check_balance",
      "requires_approval": false
    },
    {
      "step_id": "2",
      "type": "policy_check",
      "requires_approval": false
    },
    {
      "step_id": "3",
      "type": "onchain_action",
      "requires_approval": true
    }
  ]
}
```

## Environment Variables

- `PORT` - Service port (default: 8000)
- `REDIS_URL` - Redis connection URL
- `QUBIC_SERVICE_URL` - Qubic service URL
- `AGENT_RUNTIME_URL` - Agent runtime service URL
- `LOG_LEVEL` - Logging level (default: INFO)

## Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

