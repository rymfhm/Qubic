"""
Agent Runtime Service
Nostramos multi-agent orchestration runtime
"""

import os
import logging
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import redis
import json
import uuid
from datetime import datetime
from enum import Enum

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agent Runtime", version="1.0.0")

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
WORKER_SERVICE_URL = os.getenv("WORKER_SERVICE_URL", "http://localhost:8003")
AUDIT_SERVICE_URL = os.getenv("AUDIT_SERVICE_URL", "http://localhost:8002")

# Redis client
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Agent types
class AgentType(str, Enum):
    PLANNER = "planner_agent"
    EXECUTION = "execution_agent"
    AUDIT = "audit_agent"
    COMPLIANCE = "compliance_agent"

# Task status
class TaskStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"

# Request/Response models
class PlanExecuteRequest(BaseModel):
    task_id: str
    plan: Dict[str, Any]

class StepExecution(BaseModel):
    step_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    current_step: int
    total_steps: int
    steps: List[StepExecution]
    requires_approval: bool

class ApprovalRequest(BaseModel):
    approved: bool
    reason: str
    user_id: str

# Agent registry (simplified Nostramos-style)
class AgentRegistry:
    def __init__(self):
        self.agents = {}
    
    def register(self, agent_type: AgentType, handler_func):
        """Register an agent handler"""
        self.agents[agent_type.value] = handler_func
        logger.info(f"Registered agent: {agent_type.value}")
    
    async def dispatch(self, agent_type: str, task_id: str, step: Dict, context: Dict) -> Dict:
        """Dispatch task to agent"""
        if agent_type not in self.agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        handler = self.agents[agent_type]
        return await handler(task_id, step, context)

# Global agent registry
agent_registry = AgentRegistry()

# Agent handlers
async def planner_agent_handler(task_id: str, step: Dict, context: Dict) -> Dict:
    """Planner agent - validates plan structure"""
    logger.info(f"Planner agent processing step {step.get('step_id')} for task {task_id}")
    return {
        "status": "success",
        "result": {"validated": True}
    }

async def execution_agent_handler(task_id: str, step: Dict, context: Dict) -> Dict:
    """Execution agent - dispatches to worker service"""
    logger.info(f"Execution agent processing step {step.get('step_id')} for task {task_id}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{WORKER_SERVICE_URL}/execute",
                json={
                    "task_id": task_id,
                    "step": step,
                    "context": context
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Execution agent failed: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

async def audit_agent_handler(task_id: str, step: Dict, context: Dict) -> Dict:
    """Audit agent - records execution in audit service"""
    logger.info(f"Audit agent processing step {step.get('step_id')} for task {task_id}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{AUDIT_SERVICE_URL}/audit/record",
                json={
                    "task_id": task_id,
                    "step_index": int(step.get("step_id", 0)),
                    "step_type": step.get("type"),
                    "input_data": context.get("input_data", {}),
                    "output_data": context.get("output_data", {})
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Audit agent failed: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

async def compliance_agent_handler(task_id: str, step: Dict, context: Dict) -> Dict:
    """Compliance agent - checks compliance rules"""
    logger.info(f"Compliance agent processing step {step.get('step_id')} for task {task_id}")
    
    # Check if step requires approval
    requires_approval = step.get("requires_approval", False)
    
    if requires_approval:
        # Check if approval exists
        approval_key = f"approval:{task_id}:{step.get('step_id')}"
        approval = redis_client.get(approval_key)
        
        if not approval:
            return {
                "status": "waiting_approval",
                "requires_approval": True
            }
        
        approval_data = json.loads(approval)
        if not approval_data.get("approved", False):
            return {
                "status": "rejected",
                "reason": approval_data.get("reason", "Not approved")
            }
    
    return {
        "status": "compliant",
        "approved": True
    }

# Register agents
agent_registry.register(AgentType.PLANNER, planner_agent_handler)
agent_registry.register(AgentType.EXECUTION, execution_agent_handler)
agent_registry.register(AgentType.AUDIT, audit_agent_handler)
agent_registry.register(AgentType.COMPLIANCE, compliance_agent_handler)

# Plan execution logic
async def execute_plan(task_id: str, plan: Dict) -> Dict:
    """Execute plan steps sequentially"""
    steps = plan.get("steps", [])
    total_steps = len(steps)
    
    # Initialize task state
    task_state = {
        "task_id": task_id,
        "status": TaskStatus.EXECUTING.value,
        "current_step": 0,
        "total_steps": total_steps,
        "steps": [],
        "context": {}
    }
    
    redis_client.hset(f"task_runtime:{task_id}", mapping={
        "status": task_state["status"],
        "current_step": str(task_state["current_step"]),
        "total_steps": str(total_steps),
        "steps": json.dumps([])
    })
    
    for idx, step in enumerate(steps):
        step_id = step.get("step_id", str(idx + 1))
        logger.info(f"Executing step {step_id} for task {task_id}")
        
        # Update current step
        task_state["current_step"] = idx + 1
        redis_client.hset(f"task_runtime:{task_id}", "current_step", str(idx + 1))
        
        # Compliance check
        compliance_result = await agent_registry.dispatch(
            AgentType.COMPLIANCE.value,
            task_id,
            step,
            task_state["context"]
        )
        
        if compliance_result.get("status") == "waiting_approval":
            task_state["status"] = TaskStatus.WAITING_APPROVAL.value
            redis_client.hset(f"task_runtime:{task_id}", "status", TaskStatus.WAITING_APPROVAL.value)
            break
        
        if compliance_result.get("status") == "rejected":
            task_state["status"] = TaskStatus.REJECTED.value
            redis_client.hset(f"task_runtime:{task_id}", "status", TaskStatus.REJECTED.value)
            break
        
        # Execute step
        execution_result = await agent_registry.dispatch(
            AgentType.EXECUTION.value,
            task_id,
            step,
            task_state["context"]
        )
        
        # Update context with result
        task_state["context"][f"step_{step_id}"] = execution_result
        
        # Audit step
        audit_result = await agent_registry.dispatch(
            AgentType.AUDIT.value,
            task_id,
            step,
            {
                "input_data": step,
                "output_data": execution_result
            }
        )
        
        # Record step execution
        step_execution = {
            "step_id": step_id,
            "status": execution_result.get("status", "unknown"),
            "result": execution_result.get("result"),
            "error": execution_result.get("error")
        }
        
        task_state["steps"].append(step_execution)
        
        # Update Redis
        redis_client.hset(
            f"task_runtime:{task_id}",
            "steps",
            json.dumps(task_state["steps"])
        )
        
        # Check for failures
        if execution_result.get("status") == "failed":
            task_state["status"] = TaskStatus.FAILED.value
            redis_client.hset(f"task_runtime:{task_id}", "status", TaskStatus.FAILED.value)
            break
    
    # Mark as completed if all steps succeeded
    if task_state["status"] == TaskStatus.EXECUTING.value:
        task_state["status"] = TaskStatus.COMPLETED.value
        redis_client.hset(f"task_runtime:{task_id}", "status", TaskStatus.COMPLETED.value)
    
    return task_state

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return {"status": "healthy", "service": "agent-runtime"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 503

@app.post("/plan/execute")
async def execute_plan_endpoint(request: PlanExecuteRequest):
    """Execute a plan"""
    logger.info(f"Executing plan for task: {request.task_id}")
    
    # Execute plan asynchronously (in production, use background tasks)
    task_state = await execute_plan(request.task_id, request.plan)
    
    return {
        "task_id": request.task_id,
        "status": task_state["status"],
        "message": "Plan execution started"
    }

@app.get("/task/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get task execution status"""
    task_data = redis_client.hgetall(f"task_runtime:{task_id}")
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    steps = json.loads(task_data.get("steps", "[]"))
    current_step = int(task_data.get("current_step", 0))
    total_steps = int(task_data.get("total_steps", 0))
    status = task_data.get("status", "unknown")
    
    # Check if waiting for approval
    requires_approval = status == TaskStatus.WAITING_APPROVAL.value
    
    return TaskStatusResponse(
        task_id=task_id,
        status=status,
        current_step=current_step,
        total_steps=total_steps,
        steps=[StepExecution(**step) for step in steps],
        requires_approval=requires_approval
    )

@app.post("/task/{task_id}/approve")
async def approve_task(task_id: str, request: ApprovalRequest):
    """Process approval for a task"""
    task_data = redis_client.hgetall(f"task_runtime:{task_id}")
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_data.get("status") != TaskStatus.WAITING_APPROVAL.value:
        raise HTTPException(status_code=400, detail="Task is not waiting for approval")
    
    # Store approval
    current_step = task_data.get("current_step", "0")
    approval_key = f"approval:{task_id}:{current_step}"
    approval_data = {
        "approved": request.approved,
        "reason": request.reason,
        "user_id": request.user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    redis_client.set(approval_key, json.dumps(approval_data))
    
    if request.approved:
        # Resume execution
        redis_client.hset(f"task_runtime:{task_id}", "status", TaskStatus.EXECUTING.value)
        # In production, trigger resume execution
        return {"message": "Approval granted, execution resumed"}
    else:
        redis_client.hset(f"task_runtime:{task_id}", "status", TaskStatus.REJECTED.value)
        return {"message": "Approval rejected, task stopped"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

