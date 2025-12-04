"""
Planner Service
LangGraph-based task planning service
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

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Planner Service", version="1.0.0")

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUBIC_SERVICE_URL = os.getenv("QUBIC_SERVICE_URL", "http://localhost:8001")
AGENT_RUNTIME_URL = os.getenv("AGENT_RUNTIME_URL", "http://localhost:8005")

# Redis client
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Request/Response models
class PlanRequest(BaseModel):
    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any]

class Step(BaseModel):
    step_id: str
    type: str
    requires_approval: bool = False
    parameters: Optional[Dict[str, Any]] = None

class PlanResponse(BaseModel):
    plan_id: str
    task_id: str
    steps: List[Step]
    created_at: str

# LangGraph-style state
class PlanState:
    def __init__(self, task_id: str, task_type: str, description: str, parameters: Dict):
        self.task_id = task_id
        self.task_type = task_type
        self.description = description
        self.parameters = parameters
        self.analysis_result = None
        self.policy_result = None
        self.steps = []

# LangGraph nodes (simplified implementation)
async def analyze_task(state: PlanState) -> PlanState:
    """Analyze task and determine requirements"""
    logger.info(f"Analyzing task: {state.task_type}")
    
    # Mock LLM analysis - in production, call actual LLM
    if state.task_type == "monitor_wallet":
        state.analysis_result = {
            "action_type": "monitoring",
            "risk_level": "medium",
            "requires_approval": False
        }
    elif state.task_type == "transfer_funds":
        state.analysis_result = {
            "action_type": "transaction",
            "risk_level": "high",
            "requires_approval": True
        }
    else:
        state.analysis_result = {
            "action_type": "unknown",
            "risk_level": "low",
            "requires_approval": False
        }
    
    return state

async def policy_check(state: PlanState) -> PlanState:
    """Check policy with Qubic service"""
    logger.info(f"Checking policy for task: {state.task_id}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{QUBIC_SERVICE_URL}/policy",
                params={"action_type": state.analysis_result.get("action_type", "unknown")}
            )
            response.raise_for_status()
            policy_data = response.json()
            
            state.policy_result = {
                "allowed": policy_data.get("allowed", True),
                "requires_approval": policy_data.get("requires_approval", False),
                "policy_id": policy_data.get("policy_id")
            }
            
    except httpx.HTTPError as e:
        logger.error(f"Policy check failed: {e}")
        # Default to allowing but requiring approval
        state.policy_result = {
            "allowed": True,
            "requires_approval": True,
            "policy_id": None
        }
    
    return state

async def plan_builder(state: PlanState) -> PlanState:
    """Build execution plan steps"""
    logger.info(f"Building plan for task: {state.task_id}")
    
    steps = []
    
    # Step 1: Check balance
    steps.append({
        "step_id": "1",
        "type": "check_balance",
        "requires_approval": False,
        "parameters": {
            "wallet_address": state.parameters.get("wallet_address")
        }
    })
    
    # Step 2: Policy check
    steps.append({
        "step_id": "2",
        "type": "policy_check",
        "requires_approval": False,
        "parameters": {
            "policy_id": state.policy_result.get("policy_id") if state.policy_result else None
        }
    })
    
    # Step 3: Main action (may require approval)
    if state.task_type == "monitor_wallet":
        steps.append({
            "step_id": "3",
            "type": "monitor_action",
            "requires_approval": state.policy_result.get("requires_approval", False) if state.policy_result else False,
            "parameters": state.parameters
        })
    elif state.task_type == "transfer_funds":
        steps.append({
            "step_id": "3",
            "type": "onchain_action",
            "requires_approval": True,  # Always require approval for transfers
            "parameters": state.parameters
        })
    else:
        steps.append({
            "step_id": "3",
            "type": "generic_action",
            "requires_approval": state.policy_result.get("requires_approval", False) if state.policy_result else False,
            "parameters": state.parameters
        })
    
    state.steps = steps
    return state

# Simplified LangGraph execution
async def execute_plan_graph(task_id: str, task_type: str, description: str, parameters: Dict) -> Dict:
    """Execute LangGraph-style planning graph"""
    state = PlanState(task_id, task_type, description, parameters)
    
    # Execute nodes in sequence
    state = await analyze_task(state)
    state = await policy_check(state)
    state = await plan_builder(state)
    
    return {
        "steps": state.steps,
        "analysis": state.analysis_result,
        "policy": state.policy_result
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return {"status": "healthy", "service": "planner-service"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 503

@app.post("/plan/create", response_model=PlanResponse)
async def create_plan(request: PlanRequest):
    """Create a new execution plan"""
    logger.info(f"Creating plan for task: {request.task_id}")
    
    # Execute planning graph
    plan_result = await execute_plan_graph(
        request.task_id,
        request.task_type,
        request.description,
        request.parameters
    )
    
    # Generate plan ID
    plan_id = str(uuid.uuid4())
    
    # Store plan in Redis
    plan_data = {
        "plan_id": plan_id,
        "task_id": request.task_id,
        "steps": json.dumps(plan_result["steps"]),
        "created_at": datetime.utcnow().isoformat(),
        "analysis": json.dumps(plan_result["analysis"]),
        "policy": json.dumps(plan_result["policy"])
    }
    redis_client.hset(f"plan:{plan_id}", mapping=plan_data)
    
    # Convert steps to response format
    steps = [Step(**step) for step in plan_result["steps"]]
    
    return PlanResponse(
        plan_id=plan_id,
        task_id=request.task_id,
        steps=steps,
        created_at=plan_data["created_at"]
    )

@app.get("/plan/{plan_id}")
async def get_plan(plan_id: str):
    """Get plan details"""
    plan_data = redis_client.hgetall(f"plan:{plan_id}")
    
    if not plan_data:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    steps = json.loads(plan_data.get("steps", "[]"))
    
    return {
        "plan_id": plan_id,
        "task_id": plan_data.get("task_id"),
        "steps": steps,
        "created_at": plan_data.get("created_at"),
        "analysis": json.loads(plan_data.get("analysis", "{}")),
        "policy": json.loads(plan_data.get("policy", "{}"))
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

