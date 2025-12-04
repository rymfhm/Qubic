#!/bin/bash

# Start script for audit service with migrations

echo "Running database migrations..."
cd /app
alembic upgrade head

echo "Starting audit service..."
python main.py

