# Qubic System Deployment Script (PowerShell)
# This script automates the deployment process

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Qubic Autonomous Execution System" -ForegroundColor Cyan
Write-Host "Deployment Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "Checking Docker installation..." -ForegroundColor Blue
try {
    $dockerVersion = docker --version
    $composeVersion = docker-compose --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
    Write-Host "✓ Docker Compose found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if Docker is running
Write-Host "Checking if Docker is running..." -ForegroundColor Blue
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Build and start services
Write-Host "Building and starting all services..." -ForegroundColor Blue
docker-compose up --build -d

Write-Host ""
Write-Host "Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Wait for health checks
$maxWait = 120
$waited = 0
$allHealthy = $false

while ($waited -lt $maxWait) {
    $healthyCount = (docker-compose ps | Select-String "healthy").Count
    $totalServices = 10  # Adjust based on your services
    
    if ($healthyCount -ge $totalServices) {
        $allHealthy = $true
        break
    }
    
    Write-Host "Waiting... ($waited/$maxWait seconds) - $healthyCount/$totalServices services healthy" -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    $waited += 5
}

Write-Host ""

if ($allHealthy) {
    Write-Host "✓ All services are healthy!" -ForegroundColor Green
} else {
    Write-Host "⚠ Some services may still be starting. Check with: docker-compose ps" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "  API Gateway:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  View logs:    docker-compose logs -f" -ForegroundColor White
Write-Host "  Stop:         docker-compose down" -ForegroundColor White
Write-Host "  Status:       docker-compose ps" -ForegroundColor White
Write-Host ""
Write-Host "Happy deploying! 🚀" -ForegroundColor Green

