# Frontend Setup Guide

## Overview

The frontend has been successfully connected to the Qubic Autonomous Execution System API Gateway.

## What Was Done

### 1. API Client Created (`Frontend/lib/api.js`)
- Centralized API client for all backend communication
- Connects to API Gateway at `http://localhost:8000`
- Methods for:
  - Task creation (`startTask`)
  - Task status (`getTaskStatus`)
  - Task approval (`approveTask`)
  - Audit log retrieval (`getAuditLog`)
  - Health checks (`healthCheck`)

### 2. New Tasks Page (`Frontend/app/tasks/page.jsx`)
- Complete task management interface
- Create new tasks (monitor_wallet, transfer_funds)
- Real-time task status monitoring (polls every 3 seconds)
- Approval workflow (approve/reject buttons)
- Audit log viewing with Qubic transaction IDs
- Status indicators with color coding

### 3. Updated Components
- **TaskRunner** (`Frontend/app/executions/TaskRunner.jsx`): Now uses real API
- **Home Dashboard** (`Frontend/app/dashboard/Home.jsx`): Shows real system health status

### 4. Docker Configuration
- **Dockerfile**: Multi-stage build for Next.js
- **docker-compose.yml**: Frontend service added
- **.dockerignore**: Optimized build context

### 5. Next.js Configuration
- Updated `next.config.js` for standalone output
- Environment variable support for API URL
- API rewrites configured

## Running the Frontend

### Option 1: Docker (Recommended)
```bash
# Build and start frontend
docker-compose up --build frontend

# Or start all services including frontend
docker-compose up --build
```

Frontend will be available at: **http://localhost:3000**

### Option 2: Local Development
```bash
cd Frontend
npm install
npm run dev
```

Frontend will be available at: **http://localhost:3000**

## Environment Variables

Set `NEXT_PUBLIC_API_URL` if API Gateway is not on localhost:8000:

```bash
# In docker-compose.yml or .env file
NEXT_PUBLIC_API_URL=http://your-api-gateway:8000
```

## Features

### ✅ Task Management
- Create tasks with task type, wallet address, and description
- View all created tasks
- Real-time status updates
- Task details with current step progress

### ✅ Approval Workflow
- Visual approval prompts when tasks require approval
- Approve/Reject buttons
- Real-time status updates after approval

### ✅ Audit Trail
- View complete audit logs for each task
- See Qubic transaction IDs
- Step-by-step execution history
- Hash verification status

### ✅ System Health
- Dashboard shows API Gateway health status
- Real-time health monitoring
- Service status indicators

## Navigation

The sidebar already includes a "Tasks" link that navigates to `/tasks`.

## API Integration Points

All API calls go through `lib/api.js`:

```javascript
import apiClient from '@/lib/api';

// Start a task
const task = await apiClient.startTask({
  task_type: 'monitor_wallet',
  wallet_address: '0x123...',
  description: 'Monitor wallet balance'
});

// Get task status
const status = await apiClient.getTaskStatus(taskId);

// Approve task
await apiClient.approveTask(taskId, true, 'Approved');

// Get audit log
const audit = await apiClient.getAuditLog(taskId);
```

## Troubleshooting

### Frontend can't connect to API
1. Check API Gateway is running: `docker-compose ps api-gateway`
2. Verify API URL: Check `NEXT_PUBLIC_API_URL` environment variable
3. Check browser console for CORS errors
4. Ensure API Gateway CORS is enabled (already configured)

### Build errors
1. Clear `.next` folder: `rm -rf Frontend/.next`
2. Reinstall dependencies: `cd Frontend && npm install`
3. Check Node.js version (requires Node 20+)

### Docker build fails
1. Check Dockerfile syntax
2. Verify all files are present
3. Check build logs: `docker-compose build frontend --no-cache`

## Next Steps

1. **Start the frontend**:
   ```bash
   docker-compose up --build frontend
   ```

2. **Access the application**:
   - Open http://localhost:3000
   - Navigate to "Tasks" in the sidebar
   - Create a new task
   - Monitor execution in real-time

3. **Test the workflow**:
   - Create a "monitor_wallet" task
   - Watch status updates
   - Approve if required
   - View audit logs

## Files Modified/Created

- ✅ `Frontend/lib/api.js` - API client (NEW)
- ✅ `Frontend/app/tasks/page.jsx` - Tasks page (NEW)
- ✅ `Frontend/app/executions/TaskRunner.jsx` - Updated with API
- ✅ `Frontend/app/dashboard/Home.jsx` - Updated with real health
- ✅ `Frontend/Dockerfile` - Docker configuration (NEW)
- ✅ `Frontend/.dockerignore` - Build optimization (NEW)
- ✅ `Frontend/next.config.js` - Updated configuration
- ✅ `Frontend/README.md` - Documentation (NEW)
- ✅ `docker-compose.yml` - Added frontend service

## Status

✅ **Frontend is ready and connected to the backend!**

All components are integrated and ready to use. The frontend will automatically connect to the API Gateway when both are running.

