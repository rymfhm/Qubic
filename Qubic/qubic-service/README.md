# Qubic Service

Mock Qubic blockchain service for policy management and immutable hash storage.

## Features

- Policy management and enforcement
- Immutable hash storage (simulated with Redis)
- Transaction ID generation
- Hash verification

## Endpoints

- `GET /policy` - Get policy for an action type
- `POST /write` - Write hash to Qubic
- `GET /verify/{hash}` - Verify hash exists
- `GET /tx/{txid}` - Get transaction by txid
- `GET /policies` - List all policies
- `GET /health` - Health check

## Policy Rules

The service enforces policies based on action types:

- **monitoring** - Allowed, no approval required
- **transaction** - Allowed, approval required
- **transfer_funds** - Allowed, approval required
- **unknown** - Allowed, approval required (default)

## Environment Variables

- `PORT` - Service port (default: 8000)
- `REDIS_URL` - Redis connection URL
- `LOG_LEVEL` - Logging level (default: INFO)

## Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Integration

In production, replace this mock service with actual Qubic SDK integration. The API contract should remain the same.

