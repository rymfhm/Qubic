#!/bin/bash

# Curl examples for Qubic Autonomous Execution System

API_URL="http://localhost:8000"

echo "=== API Gateway Endpoints ==="
echo ""

echo "1. Start a task:"
echo "curl -X POST $API_URL/task/start \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"task_type\": \"monitor_wallet\", \"wallet_address\": \"0x1234567890abcdef\", \"description\": \"Monitor wallet balance\"}'"
echo ""

echo "2. Get task status:"
echo "curl $API_URL/task/{task_id}"
echo ""

echo "3. Approve task:"
echo "curl -X POST $API_URL/task/{task_id}/approve \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"approved\": true, \"reason\": \"Approved for execution\"}'"
echo ""

echo "4. Get audit log:"
echo "curl $API_URL/audit/{task_id}"
echo ""

echo "5. Health check:"
echo "curl $API_URL/health"
echo ""

echo "=== Direct Service Endpoints ==="
echo ""

echo "Qubic Service (Port 8001):"
echo "curl http://localhost:8001/policy?action_type=transaction"
echo "curl http://localhost:8001/verify/{hash}"
echo ""

echo "Audit Service (Port 8002):"
echo "curl http://localhost:8002/audit/{task_id}"
echo ""

echo "Worker Service (Port 8003):"
echo "curl http://localhost:8003/health"
echo ""

echo "Planner Service (Port 8004):"
echo "curl http://localhost:8004/plan/{plan_id}"
echo ""

echo "Agent Runtime (Port 8005):"
echo "curl http://localhost:8005/task/{task_id}/status"
echo ""

