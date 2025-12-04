# Contributing

## Development Setup

1. Clone the repository
2. Install Docker and Docker Compose
3. Start infrastructure services:
   ```bash
   docker-compose up postgres redis minio
   ```

4. Set up Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. Run services locally (see individual service READMEs)

## Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and small

## Testing

- Add unit tests for new features
- Test API endpoints with curl or Postman
- Verify database migrations work correctly

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Update documentation if needed
5. Submit pull request with description

## Service-Specific Guidelines

### API Gateway
- Keep authentication logic separate
- Validate all inputs
- Return consistent error formats

### Planner Service
- Keep LangGraph nodes focused
- Document plan structure changes
- Test with various task types

### Agent Runtime
- Ensure agents are stateless
- Handle failures gracefully
- Log important state changes

### Worker Service
- Mock external services appropriately
- Hash all inputs/outputs
- Implement retry logic

### Audit Service
- Never modify audit logs
- Ensure Qubic writes succeed
- Handle database errors gracefully

### Qubic Service
- Maintain API contract
- Document policy rules
- Simulate blockchain behavior accurately

## Database Migrations

When modifying database schema:

1. Create new Alembic migration:
   ```bash
   cd audit-service
   alembic revision --autogenerate -m "description"
   ```

2. Test migration up and down
3. Verify data integrity

## Environment Variables

Document new environment variables in:
- Service README
- docker-compose.yml
- QUICKSTART.md

## Questions?

Open an issue for questions or clarifications.

