"""
Worker Service
Task execution workers with mock connectors
"""

import os
import logging
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import redis
import json
import hashlib
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Worker Service", version="1.0.0")

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
AUDIT_SERVICE_URL = os.getenv("AUDIT_SERVICE_URL", "http://localhost:8002")

# Redis client
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Request/Response models
class ExecuteRequest(BaseModel):
    task_id: str
    step: Dict[str, Any]
    context: Dict[str, Any]

class ExecuteResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None

# Mock wallet data (in production, connect to actual blockchain)
MOCK_WALLETS = {
    "0x1234567890abcdef": {
        "balance": "1000.0",
        "currency": "ETH",
        "last_updated": datetime.utcnow().isoformat()
    }
}

# Worker functions
def hash_data(data: Dict) -> str:
    """Generate SHA-256 hash of data"""
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()

async def check_balance(step: Dict, context: Dict) -> Dict:
    """Check wallet balance"""
    logger.info("Executing check_balance")
    
    wallet_address = step.get("parameters", {}).get("wallet_address")
    if not wallet_address:
        raise ValueError("wallet_address parameter required")
    
    # Mock balance check
    wallet_data = MOCK_WALLETS.get(wallet_address, {
        "balance": "0.0",
        "currency": "ETH",
        "last_updated": datetime.utcnow().isoformat()
    })
    
    return {
        "wallet_address": wallet_address,
        "balance": wallet_data["balance"],
        "currency": wallet_data["currency"],
        "timestamp": datetime.utcnow().isoformat()
    }

async def policy_check(step: Dict, context: Dict) -> Dict:
    """Policy check (already done in planner, but verify)"""
    logger.info("Executing policy_check")
    
    policy_id = step.get("parameters", {}).get("policy_id")
    
    return {
        "policy_id": policy_id,
        "status": "verified",
        "timestamp": datetime.utcnow().isoformat()
    }

async def monitor_action(step: Dict, context: Dict) -> Dict:
    """Monitor wallet action"""
    logger.info("Executing monitor_action")
    
    # Simulate monitoring
    wallet_address = step.get("parameters", {}).get("wallet_address")
    
    # Simulate breach detection
    breach_detected = True  # For demo purposes
    
    return {
        "action": "monitor",
        "wallet_address": wallet_address,
        "breach_detected": breach_detected,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Potential breach detected - approval required"
    }

async def onchain_action(step: Dict, context: Dict) -> Dict:
    """On-chain action (transaction simulation)"""
    logger.info("Executing onchain_action")
    
    # Simulate transaction
    amount = step.get("parameters", {}).get("amount", "0")
    to_address = step.get("parameters", {}).get("to_address", "")
    
    # Mock transaction simulation
    tx_hash = f"0x{hashlib.sha256(f'{step}{datetime.utcnow()}'.encode()).hexdigest()[:64]}"
    
    return {
        "action": "transaction",
        "amount": amount,
        "to_address": to_address,
        "tx_hash": tx_hash,
        "status": "simulated",
        "timestamp": datetime.utcnow().isoformat()
    }

async def generic_action(step: Dict, context: Dict) -> Dict:
    """Generic action handler"""
    logger.info("Executing generic_action")
    
    return {
        "action": "generic",
        "step_type": step.get("type"),
        "parameters": step.get("parameters", {}),
        "timestamp": datetime.utcnow().isoformat()
    }

# Step type router
STEP_HANDLERS = {
    "check_balance": check_balance,
    "policy_check": policy_check,
    "monitor_action": monitor_action,
    "onchain_action": onchain_action,
    "generic_action": generic_action
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return {"status": "healthy", "service": "worker-service"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 503

@app.post("/execute", response_model=ExecuteResponse)
async def execute_step(request: ExecuteRequest):
    """Execute a step"""
    logger.info(f"Executing step {request.step.get('step_id')} for task {request.task_id}")
    
    step_type = request.step.get("type")
    
    if step_type not in STEP_HANDLERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown step type: {step_type}"
        )
    
    handler = STEP_HANDLERS[step_type]
    
    try:
        # Execute step
        result = await handler(request.step, request.context)
        
        # Generate hashes
        input_data = {
            "step": request.step,
            "context": request.context
        }
        output_data = {
            "result": result
        }
        
        input_hash = hash_data(input_data)
        output_hash = hash_data(output_data)
        
        # Store execution record (for retry logic)
        execution_key = f"execution:{request.task_id}:{request.step.get('step_id')}"
        execution_data = {
            "task_id": request.task_id,
            "step_id": request.step.get("step_id"),
            "step_type": step_type,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "result": json.dumps(result),
            "status": "success",
            "timestamp": datetime.utcnow().isoformat()
        }
        redis_client.hset(execution_key, mapping=execution_data)
        
        # Send to audit service (with retry)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    audit_response = await client.post(
                        f"{AUDIT_SERVICE_URL}/audit/record",
                        json={
                            "task_id": request.task_id,
                            "step_index": int(request.step.get("step_id", 0)),
                            "step_type": step_type,
                            "input_data": input_data,
                            "output_data": output_data,
                            "input_hash": input_hash,
                            "output_hash": output_hash
                        }
                    )
                    audit_response.raise_for_status()
                    break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to send to audit service after {max_retries} attempts: {e}")
                else:
                    logger.warning(f"Audit service retry {attempt + 1}/{max_retries}: {e}")
                    import asyncio
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return ExecuteResponse(
            status="success",
            result=result,
            input_hash=input_hash,
            output_hash=output_hash
        )
        
    except Exception as e:
        logger.error(f"Step execution failed: {e}")
        
        # Store failure
        execution_key = f"execution:{request.task_id}:{request.step.get('step_id')}"
        execution_data = {
            "task_id": request.task_id,
            "step_id": request.step.get("step_id"),
            "step_type": step_type,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        redis_client.hset(execution_key, mapping=execution_data)
        
        return ExecuteResponse(
            status="failed",
            error=str(e)
        )

@app.get("/execution/{task_id}/{step_id}")
async def get_execution(task_id: str, step_id: str):
    """Get execution record"""
    execution_key = f"execution:{task_id}:{step_id}"
    execution_data = redis_client.hgetall(execution_key)
    
    if not execution_data:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution_data.get("result"):
        execution_data["result"] = json.loads(execution_data["result"])
    
    return execution_data

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

