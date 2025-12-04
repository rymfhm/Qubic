#!/bin/bash

# Demo script for Qubic Autonomous Execution System

echo "=== Qubic Autonomous Execution System Demo ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"

echo -e "${BLUE}Step 1: Starting a task (Monitor wallet balance)${NC}"
TASK_RESPONSE=$(curl -s -X POST "$API_URL/task/start" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "monitor_wallet",
    "wallet_address": "0x1234567890abcdef",
    "description": "Monitor wallet balance"
  }')

echo "$TASK_RESPONSE" | python -m json.tool
TASK_ID=$(echo "$TASK_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['task_id'])")

echo ""
echo -e "${GREEN}Task ID: $TASK_ID${NC}"
echo ""

sleep 2

echo -e "${BLUE}Step 2: Checking task status${NC}"
curl -s "$API_URL/task/$TASK_ID" | python -m json.tool

echo ""
sleep 2

echo -e "${BLUE}Step 3: Waiting for approval (if required)...${NC}"
sleep 3

echo -e "${YELLOW}Step 4: Approving task${NC}"
APPROVAL_RESPONSE=$(curl -s -X POST "$API_URL/task/$TASK_ID/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "reason": "Approved for execution"
  }')

echo "$APPROVAL_RESPONSE" | python -m json.tool

echo ""
sleep 3

echo -e "${BLUE}Step 5: Checking final task status${NC}"
curl -s "$API_URL/task/$TASK_ID" | python -m json.tool

echo ""
echo -e "${BLUE}Step 6: Viewing audit log${NC}"
curl -s "$API_URL/audit/$TASK_ID" | python -m json.tool

echo ""
echo -e "${GREEN}Demo completed!${NC}"

