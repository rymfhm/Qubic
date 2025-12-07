# Complete Deployment Guide
## Qubic Autonomous Execution System

This is a comprehensive, step-by-step guide for deploying the entire Qubic Autonomous Execution System from scratch. Nothing is left out.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Architecture Overview](#system-architecture-overview)
3. [Local Development Setup](#local-development-setup)
4. [Docker Deployment (Recommended)](#docker-deployment-recommended)
5. [Production Deployment](#production-deployment)
6. [Service-by-Service Configuration](#service-by-service-configuration)
7. [Database Setup and Migrations](#database-setup-and-migrations)
8. [Frontend Deployment](#frontend-deployment)
9. [Network Configuration](#network-configuration)
10. [Environment Variables Reference](#environment-variables-reference)
11. [Verification and Testing](#verification-and-testing)
12. [Troubleshooting](#troubleshooting)
13. [Maintenance and Updates](#maintenance-and-updates)

---

## Prerequisites

### Required Software

1. **Docker** (version 20.10+)
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker --version`
   - Verify: `docker-compose --version`

2. **Git** (for cloning repository)
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

3. **Node.js** (for local frontend development, optional)
   - Version: 20.x or higher
   - Download: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

4. **Python 3.11+** (for local backend development, optional)
   - Download: https://www.python.org/downloads/
   - Verify: `python --version`

### System Requirements

- **CPU**: 4 cores minimum (8+ recommended)
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 20GB free space minimum
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)

### Ports Required

Ensure these ports are available:
- `3000` - Frontend (Next.js)
- `5432` - PostgreSQL
- `6379` - Redis
- `8000` - API Gateway
- `8001` - Qubic Service
- `8002` - Audit Service
- `8003` - Worker Service
- `8004` - Planner Service
- `8005` - Agent Runtime
- `9000-9001` - MinIO

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                    (Next.js - Port 3000)                      │
└───────────────────────────┬─────────────────────────────────┘
                             │ HTTP
┌────────────────────────────▼─────────────────────────────────┐
│                    API Gateway                                │
│                   (FastAPI - Port 8000)                        │
└──────┬──────────────────────┬──────────────────────┬─────────┘
       │                      │                      │
       │                      │                      │
┌──────▼──────┐    ┌──────────▼──────────┐  ┌───────▼────────┐
│   Planner   │    │   Agent Runtime     │  │  Audit Service │
│  (Port 8004)│    │   (Port 8005)       │  │  (Port 8002)   │
└──────┬──────┘    └──────────┬──────────┘  └───────┬────────┘
       │                      │                      │
       │                      │                      │
┌──────▼──────┐    ┌──────────▼──────────┐  ┌───────▼────────┐
│   Qubic     │    │   Worker Service    │  │  PostgreSQL    │
│ (Port 8001) │    │   (Port 8003)       │  │  (Port 5432)   │
└─────────────┘    └─────────────────────┘  └─────────────────┘
                            │
                   ┌────────▼────────┐
                   │     Redis       │
                   │   (Port 6379)   │
                   └─────────────────┘
```

---

## Local Development Setup

### Step 1: Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd Qubic

# Or if already cloned, navigate to directory
cd Qubic
```

### Step 2: Verify Repository Structure

Ensure you have these directories:
```
Qubic/
├── api-gateway/
├── planner-service/
├── agent-runtime/
├── worker-service/
├── audit-service/
├── qubic-service/
├── Frontend/
├── docker-compose.yml
└── README.md
```

### Step 3: Check Docker Installation

```bash
# Verify Docker is running
docker ps

# Verify Docker Compose
docker-compose --version

# If Docker is not running, start Docker Desktop
```

---

## Docker Deployment (Recommended)

This is the **easiest and recommended** way to deploy the entire system.

### Step 1: Prepare Environment

```bash
# Navigate to project root
cd Qubic

# Create .env file (optional, for custom configuration)
# Most settings work with defaults
```

### Step 2: Build and Start All Services

```bash
# Build all Docker images and start all services
docker-compose up --build -d

# The -d flag runs in detached mode (background)
# Remove -d to see logs in real-time
```

**What this does:**
- Builds Docker images for all 6 microservices + frontend
- Pulls base images (PostgreSQL, Redis, MinIO)
- Creates Docker network
- Creates volumes for data persistence
- Starts all services in dependency order
- Runs health checks

### Step 3: Monitor Startup

```bash
# Watch all services start
docker-compose logs -f

# Or watch specific service
docker-compose logs -f api-gateway

# Check service status
docker-compose ps
```

**Expected output:**
- All services should show `(healthy)` status
- Startup takes 30-60 seconds
- Wait for all health checks to pass

### Step 4: Verify Services Are Running

```bash
# Check all containers
docker-compose ps

# You should see:
# - qubic-postgres-1 (healthy)
# - qubic-redis-1 (healthy)
# - qubic-minio-1 (healthy)
# - qubic-qubic-service-1 (healthy)
# - qubic-audit-service-1 (healthy)
# - qubic-worker-service-1 (healthy)
# - qubic-planner-service-1 (healthy)
# - qubic-agent-runtime-1 (healthy)
# - qubic-api-gateway-1 (healthy)
# - qubic-frontend-1 (healthy)
```

### Step 5: Access the Application

1. **Frontend**: http://localhost:3000
2. **API Gateway**: http://localhost:8000
3. **API Docs**: http://localhost:8000/docs (FastAPI Swagger)

### Step 6: Run Health Checks

```bash
# Test API Gateway
curl http://localhost:8000/health

# Test all services
curl http://localhost:8001/health  # Qubic
curl http://localhost:8002/health  # Audit
curl http://localhost:8003/health  # Worker
curl http://localhost:8004/health  # Planner
curl http://localhost:8005/health  # Agent Runtime
```

All should return: `{"status":"healthy","service":"..."}`

---

## Production Deployment

### Option 1: Docker Compose on Server

#### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

#### Step 2: Clone and Deploy

```bash
# Clone repository
git clone <repository-url>
cd Qubic

# Create production .env file
cat > .env << EOF
NEXT_PUBLIC_API_URL=http://your-domain.com:8000
POSTGRES_PASSWORD=your-secure-password
REDIS_PASSWORD=your-redis-password
MINIO_ROOT_USER=your-minio-user
MINIO_ROOT_PASSWORD=your-minio-password
EOF

# Build and start
docker-compose up --build -d

# Set up auto-restart
sudo systemctl enable docker
```

#### Step 3: Configure Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/qubic
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API Gateway
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/qubic /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Step 4: SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Option 2: Kubernetes Deployment

#### Step 1: Create Kubernetes Manifests

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: qubic
```

```yaml
# k8s/postgres.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: qubic
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: qubic
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_USER
          value: qubic_user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: qubic-secrets
              key: postgres-password
        - name: POSTGRES_DB
          value: qubic_db
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
```

(Similar manifests needed for all services)

#### Step 2: Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace qubic

# Create secrets
kubectl create secret generic qubic-secrets \
  --from-literal=postgres-password=your-password \
  --from-literal=redis-password=your-password \
  -n qubic

# Deploy services
kubectl apply -f k8s/ -n qubic

# Check status
kubectl get pods -n qubic
kubectl get services -n qubic
```

### Option 3: Cloud Platforms

#### AWS (ECS/EKS)

1. **Build and Push Images to ECR**:
```bash
# Create ECR repository
aws ecr create-repository --repository-name qubic-api-gateway

# Login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t qubic-api-gateway ./api-gateway
docker tag qubic-api-gateway:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/qubic-api-gateway:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/qubic-api-gateway:latest
```

2. **Create ECS Task Definition** (repeat for each service)
3. **Create ECS Service** with load balancer
4. **Configure RDS** for PostgreSQL
5. **Configure ElastiCache** for Redis

#### Google Cloud Platform (GKE)

1. **Create GKE Cluster**:
```bash
gcloud container clusters create qubic-cluster \
  --num-nodes=3 \
  --zone=us-central1-a
```

2. **Build and Push to GCR**:
```bash
# Build
docker build -t gcr.io/PROJECT_ID/qubic-api-gateway ./api-gateway

# Push
docker push gcr.io/PROJECT_ID/qubic-api-gateway
```

3. **Deploy using kubectl** (see Kubernetes section)

#### Azure (AKS)

1. **Create AKS Cluster**:
```bash
az aks create \
  --resource-group qubic-rg \
  --name qubic-cluster \
  --node-count 3
```

2. **Build and Push to ACR**:
```bash
# Create registry
az acr create --resource-group qubic-rg --name qubicregistry --sku Basic

# Build and push
az acr build --registry qubicregistry --image qubic-api-gateway:latest ./api-gateway
```

---

## Service-by-Service Configuration

### 1. PostgreSQL Database

**Purpose**: Persistent storage for tasks, approvals, and audit logs

**Configuration**:
```yaml
# In docker-compose.yml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_USER: qubic_user
    POSTGRES_PASSWORD: qubic_pass  # Change in production!
    POSTGRES_DB: qubic_db
  ports:
    - "5432:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

**Initial Setup**:
- Database is created automatically
- Migrations run automatically on audit-service startup
- No manual setup required

**Production Changes**:
- Use strong password
- Enable SSL connections
- Set up backups
- Configure connection pooling

### 2. Redis

**Purpose**: Task metadata, plans, execution state, approvals, Qubic storage

**Configuration**:
```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  # No password by default (add in production!)
```

**Production Changes**:
- Add password authentication
- Enable persistence (AOF/RDB)
- Configure memory limits
- Set up Redis Sentinel for HA

### 3. MinIO

**Purpose**: S3-compatible object storage for artifacts

**Configuration**:
```yaml
minio:
  image: minio/minio:latest
  environment:
    MINIO_ROOT_USER: minioadmin
    MINIO_ROOT_PASSWORD: minioadmin  # Change in production!
  ports:
    - "9000:9000"  # API
    - "9001:9001"  # Console
  command: server /data --console-address ":9001"
```

**Access**:
- API: http://localhost:9000
- Console: http://localhost:9001
- Default credentials: minioadmin/minioadmin

**Production Changes**:
- Change default credentials
- Enable SSL/TLS
- Configure bucket policies
- Set up lifecycle policies

### 4. Qubic Service

**Purpose**: Mock blockchain service for policies and hash storage

**Build**:
```bash
cd qubic-service
docker build -t qubic-service .
```

**Environment Variables**:
- `PORT=8000`
- `REDIS_URL=redis://redis:6379/0`
- `LOG_LEVEL=INFO`

**Production**: Replace with actual Qubic SDK integration

### 5. Audit Service

**Purpose**: Audit logging with PostgreSQL and Qubic integration

**Build**:
```bash
cd audit-service
docker build -t audit-service .
```

**Environment Variables**:
- `PORT=8000`
- `DATABASE_URL=postgresql://qubic_user:qubic_pass@postgres:5432/qubic_db`
- `REDIS_URL=redis://redis:6379/0`
- `QUBIC_SERVICE_URL=http://qubic-service:8000`
- `MINIO_ENDPOINT=minio:9000`
- `MINIO_ACCESS_KEY=minioadmin`
- `MINIO_SECRET_KEY=minioadmin`

**Migrations**:
- Run automatically on startup: `alembic upgrade head`
- Located in: `audit-service/alembic/versions/`

### 6. Worker Service

**Purpose**: Task execution workers

**Environment Variables**:
- `PORT=8000`
- `REDIS_URL=redis://redis:6379/0`
- `AUDIT_SERVICE_URL=http://audit-service:8000`

### 7. Planner Service

**Purpose**: LangGraph-based task planning

**Environment Variables**:
- `PORT=8000`
- `REDIS_URL=redis://redis:6379/0`
- `QUBIC_SERVICE_URL=http://qubic-service:8000`
- `AGENT_RUNTIME_URL=http://agent-runtime:8000`

### 8. Agent Runtime

**Purpose**: Multi-agent orchestration

**Environment Variables**:
- `PORT=8000`
- `REDIS_URL=redis://redis:6379/0`
- `WORKER_SERVICE_URL=http://worker-service:8000`
- `AUDIT_SERVICE_URL=http://audit-service:8000`

### 9. API Gateway

**Purpose**: Entry point for all requests

**Environment Variables**:
- `PORT=8000`
- `REDIS_URL=redis://redis:6379/0`
- `PLANNER_SERVICE_URL=http://planner-service:8000`
- `AGENT_RUNTIME_URL=http://agent-runtime:8000`
- `AUDIT_SERVICE_URL=http://audit-service:8000`

**CORS**: Already configured to allow all origins (adjust in production)

### 10. Frontend

**Purpose**: Next.js web interface

**Build**:
```bash
cd Frontend
docker build -t qubic-frontend .
```

**Environment Variables**:
- `NEXT_PUBLIC_API_URL=http://localhost:8000` (or your API URL)
- `NODE_ENV=production`

**Local Development**:
```bash
cd Frontend
npm install
npm run dev
# Access at http://localhost:3000
```

---

## Database Setup and Migrations

### Automatic Migrations

Migrations run automatically when audit-service starts:

```bash
# In audit-service Dockerfile
CMD ["sh", "-c", "alembic upgrade head && python main.py"]
```

### Manual Migration (if needed)

```bash
# Enter audit-service container
docker-compose exec audit-service sh

# Run migrations
cd /app
alembic upgrade head

# Check current revision
alembic current

# Create new migration
alembic revision --autogenerate -m "description"
```

### Database Schema

**Tables Created**:
1. `audit_logs` - Audit trail records
2. `tasks` - Task records
3. `approvals` - Approval records

**View Schema**:
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U qubic_user -d qubic_db

# List tables
\dt

# Describe table
\d audit_logs
\d tasks
\d approvals
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U qubic_user qubic_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U qubic_user qubic_db < backup.sql
```

---

## Frontend Deployment

### Option 1: Docker (Recommended)

Already configured in `docker-compose.yml`:

```bash
# Build and start
docker-compose up --build frontend

# Access at http://localhost:3000
```

### Option 2: Local Development

```bash
cd Frontend

# Install dependencies
npm install

# Set API URL
export NEXT_PUBLIC_API_URL=http://localhost:8000
# Or create .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev

# Build for production
npm run build
npm start
```

### Option 3: Static Export (Alternative)

```javascript
// next.config.js
const nextConfig = {
  output: 'export',
  // ...
};
```

```bash
npm run build
# Output in .next/out - deploy to any static host
```

### Option 4: Vercel/Netlify

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd Frontend
vercel

# Or connect GitHub repo to Vercel dashboard
```

---

## Network Configuration

### Docker Network

Created automatically: `qubic_default`

**Services communicate via**:
- Service names as hostnames (e.g., `http://api-gateway:8000`)
- Internal DNS resolution
- No external ports needed for inter-service communication

### Port Mapping

**External Access**:
- `3000` → Frontend
- `8000` → API Gateway
- `5432` → PostgreSQL (optional, for direct access)
- `6379` → Redis (optional, for direct access)
- `9000-9001` → MinIO

**Internal Only** (not exposed):
- Service-to-service communication uses internal network

### Firewall Rules

**Production**:
```bash
# Allow only necessary ports
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 22/tcp   # SSH
sudo ufw enable
```

---

## Environment Variables Reference

### Complete .env File Template

```bash
# API Gateway
PORT=8000
REDIS_URL=redis://redis:6379/0
PLANNER_SERVICE_URL=http://planner-service:8000
AGENT_RUNTIME_URL=http://agent-runtime:8000
AUDIT_SERVICE_URL=http://audit-service:8000
LOG_LEVEL=INFO

# Planner Service
PORT=8000
REDIS_URL=redis://redis:6379/0
QUBIC_SERVICE_URL=http://qubic-service:8000
AGENT_RUNTIME_URL=http://agent-runtime:8000

# Agent Runtime
PORT=8000
REDIS_URL=redis://redis:6379/0
WORKER_SERVICE_URL=http://worker-service:8000
AUDIT_SERVICE_URL=http://audit-service:8000

# Worker Service
PORT=8000
REDIS_URL=redis://redis:6379/0
AUDIT_SERVICE_URL=http://audit-service:8000

# Audit Service
PORT=8000
DATABASE_URL=postgresql://qubic_user:qubic_pass@postgres:5432/qubic_db
REDIS_URL=redis://redis:6379/0
QUBIC_SERVICE_URL=http://qubic-service:8000
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Qubic Service
PORT=8000
REDIS_URL=redis://redis:6379/0

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=production

# PostgreSQL
POSTGRES_USER=qubic_user
POSTGRES_PASSWORD=qubic_pass
POSTGRES_DB=qubic_db

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
```

**Note**: In `docker-compose.yml`, these are set per-service. For production, use secrets management.

---

## Verification and Testing

### Step 1: Health Checks

```bash
# Run comprehensive test
cd scripts
./test-all.ps1  # Windows PowerShell
# or
./test-all.sh   # Linux/Mac

# Manual checks
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
```

### Step 2: Create Test Task

```bash
# Via API
curl -X POST http://localhost:8000/task/start \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "monitor_wallet",
    "wallet_address": "0x1234567890abcdef",
    "description": "Test task"
  }'

# Save task_id from response
```

### Step 3: Check Task Status

```bash
# Replace {task_id} with actual ID
curl http://localhost:8000/task/{task_id}
```

### Step 4: View Audit Log

```bash
curl http://localhost:8000/audit/{task_id}
```

### Step 5: Frontend Test

1. Open http://localhost:3000
2. Navigate to "Tasks" in sidebar
3. Create a new task
4. Monitor execution
5. Approve if required
6. View audit log

### Step 6: Database Verification

```bash
# Connect to database
docker-compose exec postgres psql -U qubic_user -d qubic_db

# Check tables
SELECT * FROM tasks LIMIT 5;
SELECT * FROM audit_logs LIMIT 5;
SELECT * FROM approvals LIMIT 5;
```

### Step 7: Redis Verification

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check keys
KEYS *

# Get task data
HGETALL task:{task_id}
```

---

## Troubleshooting

### Service Won't Start

**Check logs**:
```bash
docker-compose logs [service-name]
docker-compose logs --tail=50 api-gateway
```

**Common issues**:
1. **Port already in use**:
   ```bash
   # Find process using port
   lsof -i :8000  # Linux/Mac
   netstat -ano | findstr :8000  # Windows
   
   # Kill process or change port in docker-compose.yml
   ```

2. **Database connection failed**:
   ```bash
   # Check PostgreSQL is running
   docker-compose ps postgres
   
   # Check connection
   docker-compose exec postgres psql -U qubic_user -d qubic_db -c "SELECT 1;"
   ```

3. **Redis connection failed**:
   ```bash
   # Check Redis is running
   docker-compose ps redis
   
   # Test connection
   docker-compose exec redis redis-cli ping
   ```

### Frontend Can't Connect to API

1. **Check API Gateway is running**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check CORS** (already configured, but verify):
   - API Gateway has CORS middleware enabled

3. **Check API URL**:
   - Verify `NEXT_PUBLIC_API_URL` in frontend environment
   - Check browser console for errors

4. **Network issues**:
   ```bash
   # From frontend container
   docker-compose exec frontend wget -O- http://api-gateway:8000/health
   ```

### Database Migration Errors

```bash
# Check migration status
docker-compose exec audit-service alembic current

# View migration history
docker-compose exec audit-service alembic history

# Rollback if needed
docker-compose exec audit-service alembic downgrade -1

# Force upgrade
docker-compose exec audit-service alembic upgrade head
```

### Out of Memory

```bash
# Check container memory
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Or add memory limits in docker-compose.yml:
services:
  api-gateway:
    deploy:
      resources:
        limits:
          memory: 512M
```

### Services Keep Restarting

```bash
# Check why service is restarting
docker-compose ps
docker-compose logs [service-name]

# Common causes:
# - Health check failing
# - Crash on startup
# - Dependency not ready
```

### Build Failures

```bash
# Clean build
docker-compose build --no-cache [service-name]

# Rebuild all
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -t test ./[service-name]
```

---

## Maintenance and Updates

### Updating Services

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up --build -d

# Or update specific service
docker-compose up --build -d api-gateway
```

### Database Backups

```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U qubic_user qubic_db > "$BACKUP_DIR/backup_$DATE.sql"

# Add to crontab for daily backups
# 0 2 * * * /path/to/backup.sh
```

### Log Management

```bash
# View logs
docker-compose logs -f [service-name]

# Export logs
docker-compose logs [service-name] > logs.txt

# Rotate logs (configure in docker-compose.yml)
services:
  api-gateway:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Monitoring

**Add Prometheus** (optional):
```yaml
# docker-compose.yml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

**Add Grafana** (optional):
```yaml
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
```

### Scaling Services

```bash
# Scale specific service
docker-compose up -d --scale worker-service=3

# Or in docker-compose.yml:
services:
  worker-service:
    deploy:
      replicas: 3
```

---

## Quick Reference Commands

### Start/Stop

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Restart specific service
docker-compose restart api-gateway

# Start specific service
docker-compose up -d api-gateway
```

### Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway

# Last 100 lines
docker-compose logs --tail=100 api-gateway
```

### Status

```bash
# Service status
docker-compose ps

# Resource usage
docker stats

# Network info
docker network inspect qubic_default
```

### Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U qubic_user -d qubic_db

# Backup
docker-compose exec postgres pg_dump -U qubic_user qubic_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U qubic_user qubic_db < backup.sql
```

### Redis

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Flush all (WARNING: deletes all data)
docker-compose exec redis redis-cli FLUSHALL
```

### Cleanup

```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune

# Remove everything (WARNING: destructive)
docker-compose down -v --rmi all
```

---

## Security Checklist for Production

- [ ] Change all default passwords
- [ ] Enable PostgreSQL SSL
- [ ] Add Redis password authentication
- [ ] Change MinIO credentials
- [ ] Enable HTTPS/TLS
- [ ] Implement proper OAuth/JWT authentication
- [ ] Add API rate limiting
- [ ] Configure firewall rules
- [ ] Set up secrets management (Vault, AWS Secrets Manager)
- [ ] Enable database backups
- [ ] Configure log rotation
- [ ] Set up monitoring and alerting
- [ ] Review and restrict CORS policies
- [ ] Enable audit logging
- [ ] Regular security updates

---

## Support and Resources

- **Documentation**: See `COMPLETE_ARCHITECTURE.md` for detailed architecture
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **System Status**: See `SYSTEM_STATUS.md`
- **Frontend Guide**: See `FRONTEND_SETUP.md`

---

## Conclusion

This guide covers everything needed to deploy the Qubic Autonomous Execution System. Follow the steps in order, and you'll have a fully operational system.

**Quick Start Summary**:
1. Install Docker
2. Clone repository
3. Run `docker-compose up --build -d`
4. Wait for health checks
5. Access http://localhost:3000

**For production**, follow the production deployment section and security checklist.

Good luck with your deployment! 🚀

