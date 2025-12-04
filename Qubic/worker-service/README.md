# Worker Service

Task execution workers that perform actual work (balance checks, transaction simulation, etc.).

## Capabilities

- **check_balance** - Check wallet balance (mock implementation)
- **policy_check** - Verify policy compliance
- **monitor_action** - Monitor wallet for breaches
- **onchain_action** - Simulate blockchain transactions
- **generic_action** - Generic action handler

## Endpoints

- `POST /execute` - Execute a step
- `GET /execution/{task_id}/{step_id}` - Get execution record
- `GET /health` - Health check

## Features

- SHA-256 hashing of inputs/outputs
- Retry logic for audit service calls
- Execution records stored in Redis
- Mock wallet data for testing

## Environment Variables

- `PORT` - Service port (default: 8000)
- `REDIS_URL` - Redis connection URL
- `AUDIT_SERVICE_URL` - Audit service URL
- `LOG_LEVEL` - Logging level (default: INFO)

## Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

