# Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- Git (optional, for cloning)

## Step 1: Start All Services

```bash
docker-compose up --build
```

This will:
- Build all service containers
- Start PostgreSQL, Redis, and MinIO
- Start all microservices
- Run database migrations automatically

Wait for all services to be healthy (about 30-60 seconds).

## Step 2: Verify Services

Check that all services are running:

```bash
# API Gateway
curl http://localhost:8000/health

# Qubic Service
curl http://localhost:8001/health

# Audit Service
curl http://localhost:8002/health

# Worker Service
curl http://localhost:8003/health

# Planner Service
curl http://localhost:8004/health

# Agent Runtime
curl http://localhost:8005/health
```

All should return `{"status": "healthy", ...}`.

## Step 3: Run Demo

### Option 1: Using Bash Script (Linux/Mac)

```bash
chmod +x scripts/demo.sh
./scripts/demo.sh
```

### Option 2: Using PowerShell Script (Windows)

```powershell
.\scripts\demo.ps1
```

### Option 3: Manual Steps

**1. Start a task:**
```bash
curl -X POST http://localhost:8000/task/start \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "monitor_wallet",
    "wallet_address": "0x1234567890abcdef",
    "description": "Monitor wallet balance"
  }'
```

Save the `task_id` from the response.

**2. Check task status:**
```bash
curl http://localhost:8000/task/{task_id}
```

**3. Approve task (if required):**
```bash
curl -X POST http://localhost:8000/task/{task_id}/approve \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "reason": "Approved for execution"
  }'
```

**4. View audit log:**
```bash
curl http://localhost:8000/audit/{task_id}
```

## Step 4: Explore Services

### View Qubic Policies

```bash
curl http://localhost:8001/policies
```

### Check Qubic Transaction

```bash
# Get txid from audit log, then:
curl http://localhost:8001/tx/{txid}
```

### View Plan Details

```bash
# Get plan_id from task status, then:
curl http://localhost:8004/plan/{plan_id}
```

## Troubleshooting

### Services Not Starting

1. Check Docker logs:
   ```bash
   docker-compose logs [service-name]
   ```

2. Verify ports are not in use:
   ```bash
   # Linux/Mac
   lsof -i :8000
   
   # Windows
   netstat -ano | findstr :8000
   ```

### Database Connection Issues

1. Wait for PostgreSQL to be ready:
   ```bash
   docker-compose logs postgres
   ```

2. Check database URL in environment variables

### Redis Connection Issues

1. Check Redis is running:
   ```bash
   docker-compose exec redis redis-cli ping
   ```

## Stopping Services

```bash
docker-compose down
```

To remove volumes (clears all data):
```bash
docker-compose down -v
```

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Check individual service READMEs for details
- Review [examples/](examples/) for sample data structures
- Explore API endpoints in [scripts/curl-examples.sh](scripts/curl-examples.sh)

## Development

To develop locally:

1. Start infrastructure only:
   ```bash
   docker-compose up postgres redis minio
   ```

2. Run services locally:
   ```bash
   cd api-gateway
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

Repeat for other services.

## Production Considerations

- Replace mock Qubic service with real SDK
- Implement proper OAuth/JWT authentication
- Add rate limiting and API keys
- Set up monitoring and alerting
- Configure SSL/TLS
- Use secrets management (Vault, AWS Secrets Manager)
- Set up CI/CD pipeline
- Add comprehensive logging and tracing

