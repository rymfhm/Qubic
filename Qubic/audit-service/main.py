"""
Audit Service
Audit logging with Qubic blockchain integration
"""

import os
import logging
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import hashlib
import json

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Audit Service", version="1.0.0")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://qubic_user:qubic_pass@localhost:5432/qubic_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    task_type = Column(String)
    status = Column(String)
    plan_id = Column(String, nullable=True)
    user_id = Column(String)
    description = Column(Text)
    parameters = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True)
    step_id = Column(String)
    approved = Column(Boolean)
    reason = Column(Text)
    user_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True)
    step_index = Column(Integer)
    step_type = Column(String)
    input_hash = Column(String, index=True)
    output_hash = Column(String, index=True)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    qubic_txid = Column(String, nullable=True)
    metadata_json = Column(Text)  # JSON string (renamed from 'metadata' to avoid SQLAlchemy conflict)

# Tables are created via Alembic migrations, not here

# Configuration
QUBIC_SERVICE_URL = os.getenv("QUBIC_SERVICE_URL", "http://localhost:8001")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

# Request/Response models
class AuditRecordRequest(BaseModel):
    task_id: str
    step_index: int
    step_type: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None

class AuditRecordResponse(BaseModel):
    id: int
    task_id: str
    step_index: int
    input_hash: str
    output_hash: str
    qubic_txid: Optional[str] = None

class AuditLogResponse(BaseModel):
    task_id: str
    logs: List[Dict[str, Any]]
    qubic_txid: Optional[str] = None

def hash_data(data: Dict) -> str:
    """Generate SHA-256 hash of data"""
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "service": "audit-service"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 503

@app.post("/audit/record", response_model=AuditRecordResponse)
async def record_audit(request: AuditRecordRequest):
    """Record an audit log entry"""
    logger.info(f"Recording audit for task {request.task_id}, step {request.step_index}")
    
    # Generate hashes if not provided
    input_hash = request.input_hash or hash_data(request.input_data)
    output_hash = request.output_hash or hash_data(request.output_data)
    
    # Store in database
    db = SessionLocal()
    try:
        audit_log = AuditLog(
            task_id=request.task_id,
            step_index=request.step_index,
            step_type=request.step_type,
            input_hash=input_hash,
            output_hash=output_hash,
            status="recorded",
            metadata_json=json.dumps({
                "input_data": request.input_data,
                "output_data": request.output_data
            })
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        # Push to Qubic (with retry)
        qubic_txid = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    qubic_response = await client.post(
                        f"{QUBIC_SERVICE_URL}/write",
                        json={
                            "hash": output_hash,
                            "metadata": {
                                "task_id": request.task_id,
                                "step_index": request.step_index,
                                "step_type": request.step_type,
                                "input_hash": input_hash,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        }
                    )
                    qubic_response.raise_for_status()
                    qubic_data = qubic_response.json()
                    qubic_txid = qubic_data.get("txid")
                    break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to write to Qubic after {max_retries} attempts: {e}")
                else:
                    logger.warning(f"Qubic write retry {attempt + 1}/{max_retries}: {e}")
                    import asyncio
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # Update audit log with Qubic txid
        if qubic_txid:
            audit_log.qubic_txid = qubic_txid
            db.commit()
        
        return AuditRecordResponse(
            id=audit_log.id,
            task_id=audit_log.task_id,
            step_index=audit_log.step_index,
            input_hash=audit_log.input_hash,
            output_hash=audit_log.output_hash,
            qubic_txid=audit_log.qubic_txid
        )
    finally:
        db.close()

@app.get("/audit/{task_id}", response_model=AuditLogResponse)
async def get_audit_log(task_id: str):
    """Get audit log for a task"""
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).filter(AuditLog.task_id == task_id).order_by(AuditLog.step_index).all()
        
        if not logs:
            raise HTTPException(status_code=404, detail="Audit log not found")
        
        log_entries = []
        latest_qubic_txid = None
        
        for log in logs:
            entry = {
                "id": log.id,
                "step_index": log.step_index,
                "step_type": log.step_type,
                "input_hash": log.input_hash,
                "output_hash": log.output_hash,
                "status": log.status,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "qubic_txid": log.qubic_txid
            }
            log_entries.append(entry)
            
            if log.qubic_txid:
                latest_qubic_txid = log.qubic_txid
        
        return AuditLogResponse(
            task_id=task_id,
            logs=log_entries,
            qubic_txid=latest_qubic_txid
        )
    finally:
        db.close()

@app.get("/audit/verify/{hash}")
async def verify_hash(hash: str):
    """Verify hash in Qubic"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{QUBIC_SERVICE_URL}/verify/{hash}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Hash verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

