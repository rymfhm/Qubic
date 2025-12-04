# API Contracts

## API Gateway (Port 8000)

### POST /task/start

Start a new task.

**Request:**
```json
{
  "task_type": "monitor_wallet",
  "wallet_address": "0x1234567890abcdef",
  "description": "Monitor wallet balance",
  "parameters": {
    "alert_threshold": 100.0
  }
}
```

**Response:**
```json
{
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "status": "executing",
  "message": "Task started successfully"
}
```

### GET /task/{task_id}

Get task status.

**Response:**
```json
{
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "status": "executing",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:05Z",
  "plan_id": "plan_87654321-4321-4321-4321-cba987654321",
  "current_step": 2,
  "requires_approval": false
}
```

### POST /task/{task_id}/approve

Approve or reject a task.

**Request:**
```json
{
  "approved": true,
  "reason": "Approved for execution"
}
```

**Response:**
```json
{
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "approved": true,
  "message": "Approval processed successfully"
}
```

### GET /audit/{task_id}

Get audit log for a task.

**Response:**
```json
{
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "logs": [
    {
      "id": 1,
      "step_index": 1,
      "step_type": "check_balance",
      "input_hash": "a1b2c3d4...",
      "output_hash": "b2c3d4e5...",
      "status": "recorded",
      "timestamp": "2024-01-01T12:00:05Z",
      "qubic_txid": "qubic_tx_abc123..."
    }
  ],
  "qubic_txid": "qubic_tx_abc123..."
}
```

## Planner Service (Port 8004)

### POST /plan/create

Create a new execution plan.

**Request:**
```json
{
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "task_type": "monitor_wallet",
  "description": "Monitor wallet balance",
  "parameters": {
    "wallet_address": "0x1234567890abcdef"
  }
}
```

**Response:**
```json
{
  "plan_id": "plan_87654321-4321-4321-4321-cba987654321",
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "steps": [
    {
      "step_id": "1",
      "type": "check_balance",
      "requires_approval": false,
      "parameters": {
        "wallet_address": "0x1234567890abcdef"
      }
    },
    {
      "step_id": "2",
      "type": "policy_check",
      "requires_approval": false
    },
    {
      "step_id": "3",
      "type": "monitor_action",
      "requires_approval": true
    }
  ],
  "created_at": "2024-01-01T12:00:00Z"
}
```

### GET /plan/{plan_id}

Get plan details.

**Response:**
```json
{
  "plan_id": "plan_87654321-4321-4321-4321-cba987654321",
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "steps": [...],
  "created_at": "2024-01-01T12:00:00Z",
  "analysis": {
    "action_type": "monitoring",
    "risk_level": "medium"
  },
  "policy": {
    "allowed": true,
    "requires_approval": false
  }
}
```

## Agent Runtime (Port 8005)

### POST /plan/execute

Execute a plan.

**Request:**
```json
{
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "plan": {
    "plan_id": "plan_87654321-4321-4321-4321-cba987654321",
    "steps": [...]
  }
}
```

**Response:**
```json
{
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "status": "executing",
  "message": "Plan execution started"
}
```

### GET /task/{task_id}/status

Get task execution status.

**Response:**
```json
{
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "status": "executing",
  "current_step": 2,
  "total_steps": 3,
  "steps": [
    {
      "step_id": "1",
      "status": "success",
      "result": {...},
      "error": null
    }
  ],
  "requires_approval": false
}
```

### POST /task/{task_id}/approve

Process approval for a task.

**Request:**
```json
{
  "approved": true,
  "reason": "Approved for execution",
  "user_id": "demo_user"
}
```

## Worker Service (Port 8003)

### POST /execute

Execute a step.

**Request:**
```json
{
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "step": {
    "step_id": "1",
    "type": "check_balance",
    "parameters": {
      "wallet_address": "0x1234567890abcdef"
    }
  },
  "context": {}
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "wallet_address": "0x1234567890abcdef",
    "balance": "1000.0",
    "currency": "ETH"
  },
  "input_hash": "a1b2c3d4...",
  "output_hash": "b2c3d4e5..."
}
```

## Audit Service (Port 8002)

### POST /audit/record

Record an audit log entry.

**Request:**
```json
{
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "step_index": 1,
  "step_type": "check_balance",
  "input_data": {...},
  "output_data": {...},
  "input_hash": "a1b2c3d4...",
  "output_hash": "b2c3d4e5..."
}
```

**Response:**
```json
{
  "id": 1,
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "step_index": 1,
  "input_hash": "a1b2c3d4...",
  "output_hash": "b2c3d4e5...",
  "qubic_txid": "qubic_tx_abc123..."
}
```

### GET /audit/{task_id}

Get audit log for a task.

**Response:**
```json
{
  "task_id": "task_12345678-1234-1234-1234-123456789abc",
  "logs": [...],
  "qubic_txid": "qubic_tx_abc123..."
}
```

## Qubic Service (Port 8001)

### GET /policy

Get policy for an action type.

**Query Parameters:**
- `action_type` (required): Action type to check

**Response:**
```json
{
  "policy_id": "policy_monitoring_abc12345",
  "action_type": "monitoring",
  "allowed": true,
  "requires_approval": false,
  "rules": {
    "allowed": true,
    "requires_approval": false,
    "risk_level": "low"
  }
}
```

### POST /write

Write hash to Qubic.

**Request:**
```json
{
  "hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "metadata": {
    "task_id": "task_12345678-1234-1234-1234-123456789abc",
    "step_index": 1,
    "step_type": "check_balance"
  }
}
```

**Response:**
```json
{
  "txid": "qubic_tx_abc123def456ghi789jkl012mno345pqr678stu901",
  "hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "timestamp": "2024-01-01T12:00:05Z"
}
```

### GET /verify/{hash}

Verify hash exists in Qubic.

**Response:**
```json
{
  "hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "verified": true,
  "txid": "qubic_tx_abc123...",
  "timestamp": "2024-01-01T12:00:05Z"
}
```

### GET /tx/{txid}

Get transaction details by txid.

**Response:**
```json
{
  "txid": "qubic_tx_abc123...",
  "hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "timestamp": "2024-01-01T12:00:05Z",
  "metadata": {...},
  "block_height": 1704110405
}
```

## Common Status Codes

- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable

## Authentication

Currently uses stub OAuth. Include Authorization header for production:

```
Authorization: Bearer <token>
```

