# Qubic Frontend

Next.js frontend for the Qubic Autonomous Execution System.

## Features

- Task creation and management
- Real-time task status monitoring
- Approval workflow
- Audit log viewing
- Dashboard with system health

## Development

```bash
cd Frontend
npm install
npm run dev
```

The frontend will run on http://localhost:3000

## Environment Variables

- `NEXT_PUBLIC_API_URL` - API Gateway URL (default: http://localhost:8000)

## Docker

The frontend is included in docker-compose.yml and will be built automatically.

```bash
docker-compose up frontend
```

## Pages

- `/dashboard` - Main dashboard with system status
- `/tasks` - Task management and monitoring
- `/executions` - Task execution interface
- `/wallet` - Wallet management
- `/settings` - Settings

## API Integration

The frontend connects to the API Gateway at `http://localhost:8000` using the API client in `lib/api.js`.
