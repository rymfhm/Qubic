"""
API Gateway Service
FastAPI gateway with OAuth-ready authentication and REST endpoints
"""

import os
import logging
import httpx
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import redis
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Qubic API Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
PLANNER_SERVICE_URL = os.getenv("PLANNER_SERVICE_URL", "http://localhost:8004")
AGENT_RUNTIME_URL = os.getenv("AGENT_RUNTIME_URL", "http://localhost:8005")
AUDIT_SERVICE_URL = os.getenv("AUDIT_SERVICE_URL", "http://localhost:8002")

# Redis client
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Request/Response models
class TaskStartRequest(BaseModel):
    task_type: str
    wallet_address: Optional[str] = None
    description: str
    parameters: Optional[dict] = None

class TaskStartResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    created_at: str
    updated_at: str
    plan_id: Optional[str] = None
    current_step: Optional[int] = None
    requires_approval: bool = False

class ApprovalRequest(BaseModel):
    approved: bool
    reason: str

class ApprovalResponse(BaseModel):
    task_id: str
    approved: bool
    message: str

class AuditLogResponse(BaseModel):
    task_id: str
    logs: list
    qubic_txid: Optional[str] = None

# OAuth stub - simple token validation
async def verify_token(authorization: Optional[str] = Header(None)):
    """Stub OAuth token verification"""
    if authorization is None:
        # For prototype, allow requests without auth
        return {"user_id": "demo_user", "email": "demo@example.com"}
    
    # In production, validate JWT token here
    token = authorization.replace("Bearer ", "")
    # Stub: accept any token
    return {"user_id": "demo_user", "email": "demo@example.com"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return {"status": "healthy", "service": "api-gateway"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 503

@app.post("/task/start", response_model=TaskStartResponse)
async def start_task(
    request: TaskStartRequest,
    user: dict = Depends(verify_token)
):
    """Start a new task"""
    task_id = str(uuid.uuid4())
    logger.info(f"Starting task {task_id}: {request.task_type}")
    
    # Store task metadata in Redis
    task_data = {
        "task_id": task_id,
        "task_type": request.task_type,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "user_id": user["user_id"],
        "description": request.description,
        "parameters": request.parameters or {}
    }
    
    redis_client.hset(f"task:{task_id}", mapping=task_data)
    
    # Send to planner service
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            planner_response = await client.post(
                f"{PLANNER_SERVICE_URL}/plan/create",
                json={
                    "task_id": task_id,
                    "task_type": request.task_type,
                    "description": request.description,
                    "parameters": request.parameters or {}
                }
            )
            planner_response.raise_for_status()
            plan_data = planner_response.json()
            
            # Update task with plan_id
            redis_client.hset(f"task:{task_id}", "plan_id", plan_data.get("plan_id", ""))
            redis_client.hset(f"task:{task_id}", "status", "planning")
            
            # Send plan to agent runtime
            runtime_response = await client.post(
                f"{AGENT_RUNTIME_URL}/plan/execute",
                json={
                    "task_id": task_id,
                    "plan": plan_data
                }
            )
            runtime_response.raise_for_status()
            
            redis_client.hset(f"task:{task_id}", "status", "executing")
            
    except httpx.HTTPError as e:
        logger.error(f"Error starting task: {e}")
        redis_client.hset(f"task:{task_id}", "status", "failed")
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")
    
    return TaskStartResponse(
        task_id=task_id,
        status="executing",
        message="Task started successfully"
    )

@app.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    user: dict = Depends(verify_token)
):
    """Get task status"""
    task_data = redis_client.hgetall(f"task:{task_id}")
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check with agent runtime for latest status
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            runtime_response = await client.get(
                f"{AGENT_RUNTIME_URL}/task/{task_id}/status"
            )
            if runtime_response.status_code == 200:
                runtime_data = runtime_response.json()
                task_data.update(runtime_data)
    except Exception as e:
        logger.warning(f"Could not fetch runtime status: {e}")
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task_data.get("status", "unknown"),
        created_at=task_data.get("created_at", ""),
        updated_at=task_data.get("updated_at", ""),
        plan_id=task_data.get("plan_id"),
        current_step=int(task_data.get("current_step", 0)) if task_data.get("current_step") else None,
        requires_approval=task_data.get("requires_approval", "false").lower() == "true"
    )

@app.post("/task/{task_id}/approve", response_model=ApprovalResponse)
async def approve_task(
    task_id: str,
    request: ApprovalRequest,
    user: dict = Depends(verify_token)
):
    """Approve or reject a task"""
    task_data = redis_client.hgetall(f"task:{task_id}")
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Send approval to agent runtime
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{AGENT_RUNTIME_URL}/task/{task_id}/approve",
                json={
                    "approved": request.approved,
                    "reason": request.reason,
                    "user_id": user["user_id"]
                }
            )
            response.raise_for_status()
            
            # Update task status
            redis_client.hset(f"task:{task_id}", "status", "approved" if request.approved else "rejected")
            redis_client.hset(f"task:{task_id}", "updated_at", datetime.utcnow().isoformat())
            
    except httpx.HTTPError as e:
        logger.error(f"Error approving task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process approval: {str(e)}")
    
    return ApprovalResponse(
        task_id=task_id,
        approved=request.approved,
        message="Approval processed successfully"
    )

@app.get("/audit/{task_id}", response_model=AuditLogResponse)
async def get_audit_log(
    task_id: str,
    user: dict = Depends(verify_token)
):
    """Get audit log for a task"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{AUDIT_SERVICE_URL}/audit/{task_id}"
            )
            response.raise_for_status()
            audit_data = response.json()
            
            return AuditLogResponse(
                task_id=task_id,
                logs=audit_data.get("logs", []),
                qubic_txid=audit_data.get("qubic_txid")
            )
    except httpx.HTTPError as e:
        logger.error(f"Error fetching audit log: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit log: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

