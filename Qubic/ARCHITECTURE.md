# Architecture Documentation

## System Overview

The Qubic Autonomous Execution System is a microservices-based platform for AI-driven task execution with blockchain-based auditing and governance.

## Service Architecture

```
┌─────────────┐
│ API Gateway │ (Port 8000)
└──────┬──────┘
       │
       ├───► Planner Service (Port 8004)
       │     └───► Qubic Service (Port 8001)
       │
       ├───► Agent Runtime (Port 8005)
       │     ├───► Worker Service (Port 8003)
       │     └───► Audit Service (Port 8002)
       │           └───► Qubic Service (Port 8001)
       │
       └───► Audit Service (Port 8002)
             └───► Qubic Service (Port 8001)
```

## Service Details

### 1. API Gateway (Port 8000)

**Technology:** FastAPI

**Responsibilities:**
- OAuth-ready authentication (stub implementation)
- REST API endpoints
- Task lifecycle management
- Approval workflow
- Audit log access

**Endpoints:**
- `POST /task/start` - Start new task
- `GET /task/{id}` - Get task status
- `POST /task/{id}/approve` - Approve/reject task
- `GET /audit/{task_id}` - Get audit log
- `GET /health` - Health check

**Dependencies:**
- Redis (task metadata)
- Planner Service
- Agent Runtime
- Audit Service

### 2. Planner Service (Port 8004)

**Technology:** LangGraph (simplified implementation)

**Responsibilities:**
- Convert user tasks to execution plans
- Task analysis
- Policy checking
- Plan generation

**LangGraph Nodes:**
1. `analyze_task` - Analyze task requirements
2. `policy_check` - Check Qubic policies
3. `plan_builder` - Generate execution steps

**Plan Structure:**
```json
{
  "plan_id": "...",
  "steps": [
    {"step_id": "1", "type": "check_balance"},
    {"step_id": "2", "type": "policy_check"},
    {"step_id": "3", "type": "onchain_action", "requires_approval": true}
  ]
}
```

**Dependencies:**
- Redis (plan storage)
- Qubic Service (policy checks)
- Agent Runtime (plan dispatch)

### 3. Agent Runtime (Port 8005)

**Technology:** Nostramos-style orchestration

**Responsibilities:**
- Multi-agent coordination
- Plan execution
- Step dispatch
- Approval enforcement
- Retry logic

**Agents:**
1. `planner_agent` - Plan validation
2. `execution_agent` - Task execution
3. `audit_agent` - Audit recording
4. `compliance_agent` - Approval checks

**Execution Flow:**
1. Receive plan from planner
2. Execute steps sequentially
3. Check compliance/approvals
4. Dispatch to workers
5. Record audit logs
6. Handle failures and retries

**Dependencies:**
- Redis (execution state)
- Worker Service
- Audit Service

### 4. Worker Service (Port 8003)

**Technology:** FastAPI

**Responsibilities:**
- Execute actual work
- Balance checks
- Transaction simulation
- Hash generation
- Result reporting

**Step Types:**
- `check_balance` - Wallet balance check
- `policy_check` - Policy verification
- `monitor_action` - Wallet monitoring
- `onchain_action` - Blockchain transaction simulation
- `generic_action` - Generic handler

**Features:**
- SHA-256 hashing
- Retry logic for audit calls
- Execution records in Redis

**Dependencies:**
- Redis (execution records)
- Audit Service (result logging)

### 5. Audit Service (Port 8002)

**Technology:** FastAPI + SQLAlchemy + PostgreSQL

**Responsibilities:**
- SHA-256 hash generation
- PostgreSQL persistence
- Qubic blockchain integration
- Audit log retrieval
- Hash verification

**Database Schema:**
- `tasks` - Task records
- `approvals` - Approval records
- `audit_logs` - Audit log entries

**Features:**
- Immutable audit trail
- Qubic transaction IDs
- Retry logic for Qubic writes

**Dependencies:**
- PostgreSQL
- Qubic Service
- MinIO (for artifacts, future)

### 6. Qubic Service (Port 8001)

**Technology:** FastAPI (Mock implementation)

**Responsibilities:**
- Policy management
- Immutable hash storage
- Transaction ID generation
- Hash verification

**Endpoints:**
- `GET /policy` - Get policy rules
- `POST /write` - Write hash to blockchain
- `GET /verify/{hash}` - Verify hash
- `GET /tx/{txid}` - Get transaction

**Policy Rules:**
- `monitoring` - Allowed, no approval
- `transaction` - Allowed, approval required
- `transfer_funds` - Allowed, approval required

**Storage:**
- Redis (simulating immutable blockchain)

**Note:** This is a mock implementation. In production, replace with actual Qubic SDK.

## Data Flow

### Task Execution Flow

1. **User Request** → API Gateway
2. **API Gateway** → Planner Service (create plan)
3. **Planner Service** → Qubic Service (policy check)
4. **Planner Service** → Agent Runtime (execute plan)
5. **Agent Runtime** → Worker Service (execute step)
6. **Worker Service** → Audit Service (record result)
7. **Audit Service** → Qubic Service (write hash)
8. **Agent Runtime** → API Gateway (status update)

### Approval Flow

1. **Agent Runtime** detects `requires_approval: true`
2. **Agent Runtime** sets status to `waiting_approval`
3. **User** calls `POST /task/{id}/approve`
4. **API Gateway** → Agent Runtime (process approval)
5. **Agent Runtime** resumes execution if approved

## Security

### Authentication
- OAuth stub (ready for JWT integration)
- Token validation in API Gateway

### Data Protection
- SHA-256 hashing of all inputs/outputs
- No PII stored in database
- Secrets via environment variables

### Policy Enforcement
- Qubic is authoritative for policies
- Approval required for high-risk actions
- Immutable audit trail

## Scalability

### Horizontal Scaling
- Stateless services (except database)
- Redis for shared state
- Docker containers

### Retry Logic
- Exponential backoff
- Configurable retry counts
- Failure tracking

## Monitoring

### Health Checks
- All services expose `/health` endpoint
- Docker health checks configured
- Database connection checks

### Logging
- Structured logging
- Configurable log levels
- Service identification

## Deployment

### Docker Compose
- All services containerized
- Health check dependencies
- Volume persistence for data

### Environment Variables
- Service URLs
- Database credentials
- Redis URLs
- Log levels

## Future Enhancements

1. **Real Qubic Integration** - Replace mock service
2. **MinIO Integration** - Store large artifacts
3. **Background Tasks** - Async execution
4. **Metrics** - Prometheus/Grafana
5. **Distributed Tracing** - OpenTelemetry
6. **Rate Limiting** - API protection
7. **WebSocket** - Real-time status updates

