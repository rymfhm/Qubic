#!/bin/bash

# Qubic System Deployment Script
# This script automates the deployment process

set -e  # Exit on error

echo "=========================================="
echo "Qubic Autonomous Execution System"
echo "Deployment Script"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Docker
echo -e "${BLUE}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose found${NC}"
echo ""

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo -e "${RED}Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Build and start services
echo -e "${BLUE}Building and starting all services...${NC}"
docker-compose up --build -d

echo ""
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Wait for health checks
MAX_WAIT=120
WAITED=0
ALL_HEALTHY=false

while [ $WAITED -lt $MAX_WAIT ]; do
    HEALTHY_COUNT=$(docker-compose ps | grep -c "healthy" || true)
    TOTAL_SERVICES=10  # Adjust based on your services
    
    if [ "$HEALTHY_COUNT" -ge "$TOTAL_SERVICES" ]; then
        ALL_HEALTHY=true
        break
    fi
    
    echo -e "${YELLOW}Waiting... ($WAITED/$MAX_WAIT seconds) - $HEALTHY_COUNT/$TOTAL_SERVICES services healthy${NC}"
    sleep 5
    WAITED=$((WAITED + 5))
done

echo ""

if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}✓ All services are healthy!${NC}"
else
    echo -e "${YELLOW}⚠ Some services may still be starting. Check with: docker-compose ps${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Services:"
echo "  Frontend:     http://localhost:3000"
echo "  API Gateway:  http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Status:       docker-compose ps"
echo ""
echo -e "${GREEN}Happy deploying! 🚀${NC}"

