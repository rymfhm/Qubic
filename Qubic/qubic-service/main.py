"""
Qubic Service
Mock Qubic blockchain service for policy and hash storage
"""

import os
import logging
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
import hashlib
import json
from datetime import datetime
import redis

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Qubic Service", version="1.0.0")

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Redis client for persistent storage (simulating blockchain)
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Request/Response models
class WriteRequest(BaseModel):
    hash: str
    metadata: Dict[str, Any]

class WriteResponse(BaseModel):
    txid: str
    hash: str
    timestamp: str

class PolicyResponse(BaseModel):
    policy_id: str
    action_type: str
    allowed: bool
    requires_approval: bool
    rules: Dict[str, Any]

class VerifyResponse(BaseModel):
    hash: str
    verified: bool
    txid: Optional[str] = None
    timestamp: Optional[str] = None

# Policy rules (simulating Qubic policy engine)
POLICY_RULES = {
    "monitoring": {
        "allowed": True,
        "requires_approval": False,
        "risk_level": "low"
    },
    "transaction": {
        "allowed": True,
        "requires_approval": True,
        "risk_level": "high",
        "max_amount": 1000.0
    },
    "transfer_funds": {
        "allowed": True,
        "requires_approval": True,
        "risk_level": "high"
    },
    "unknown": {
        "allowed": True,
        "requires_approval": True,
        "risk_level": "medium"
    }
}

def generate_txid(hash: str, metadata: Dict) -> str:
    """Generate a mock transaction ID"""
    data = f"{hash}{json.dumps(metadata, sort_keys=True)}{datetime.utcnow().isoformat()}"
    return f"qubic_tx_{hashlib.sha256(data.encode()).hexdigest()[:32]}"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return {"status": "healthy", "service": "qubic-service"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 503

@app.get("/policy", response_model=PolicyResponse)
async def get_policy(action_type: str = Query(..., description="Action type to check")):
    """Get policy for an action type"""
    logger.info(f"Checking policy for action type: {action_type}")
    
    # Get policy rules
    policy = POLICY_RULES.get(action_type, POLICY_RULES["unknown"])
    
    policy_id = f"policy_{action_type}_{hashlib.md5(action_type.encode()).hexdigest()[:8]}"
    
    return PolicyResponse(
        policy_id=policy_id,
        action_type=action_type,
        allowed=policy["allowed"],
        requires_approval=policy["requires_approval"],
        rules=policy
    )

@app.post("/write", response_model=WriteResponse)
async def write_hash(request: WriteRequest):
    """Write hash to Qubic (mock blockchain)"""
    logger.info(f"Writing hash to Qubic: {request.hash[:16]}...")
    
    # Generate transaction ID
    txid = generate_txid(request.hash, request.metadata)
    timestamp = datetime.utcnow().isoformat()
    
    # Store in Redis (simulating immutable blockchain storage)
    qubic_key = f"qubic:hash:{request.hash}"
    qubic_data = {
        "hash": request.hash,
        "txid": txid,
        "metadata": json.dumps(request.metadata),
        "timestamp": timestamp,
        "block_height": int(datetime.utcnow().timestamp())  # Mock block height
    }
    redis_client.hset(qubic_key, mapping=qubic_data)
    
    # Also store by txid for lookup
    tx_key = f"qubic:tx:{txid}"
    redis_client.hset(tx_key, mapping={
        "hash": request.hash,
        "timestamp": timestamp
    })
    
    logger.info(f"Hash written to Qubic with txid: {txid}")
    
    return WriteResponse(
        txid=txid,
        hash=request.hash,
        timestamp=timestamp
    )

@app.get("/verify/{hash}", response_model=VerifyResponse)
async def verify_hash(hash: str):
    """Verify hash exists in Qubic"""
    logger.info(f"Verifying hash: {hash[:16]}...")
    
    qubic_key = f"qubic:hash:{hash}"
    qubic_data = redis_client.hgetall(qubic_key)
    
    if not qubic_data:
        return VerifyResponse(
            hash=hash,
            verified=False
        )
    
    return VerifyResponse(
        hash=hash,
        verified=True,
        txid=qubic_data.get("txid"),
        timestamp=qubic_data.get("timestamp")
    )

@app.get("/tx/{txid}")
async def get_transaction(txid: str):
    """Get transaction details by txid"""
    tx_key = f"qubic:tx:{txid}"
    tx_data = redis_client.hgetall(tx_key)
    
    if not tx_data:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Get full hash data
    hash = tx_data.get("hash")
    qubic_key = f"qubic:hash:{hash}"
    hash_data = redis_client.hgetall(qubic_key)
    
    return {
        "txid": txid,
        "hash": hash,
        "timestamp": hash_data.get("timestamp"),
        "metadata": json.loads(hash_data.get("metadata", "{}")),
        "block_height": hash_data.get("block_height")
    }

@app.get("/policies")
async def list_policies():
    """List all policy rules"""
    policies = []
    for action_type, rules in POLICY_RULES.items():
        policy_id = f"policy_{action_type}_{hashlib.md5(action_type.encode()).hexdigest()[:8]}"
        policies.append({
            "policy_id": policy_id,
            "action_type": action_type,
            "allowed": rules["allowed"],
            "requires_approval": rules["requires_approval"],
            "risk_level": rules.get("risk_level", "unknown")
        })
    return {"policies": policies}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

