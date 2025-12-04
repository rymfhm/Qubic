# Demo script for Qubic Autonomous Execution System (PowerShell)

Write-Host "=== Qubic Autonomous Execution System Demo ===" -ForegroundColor Cyan
Write-Host ""

$API_URL = "http://localhost:8000"

Write-Host "Step 1: Starting a task (Monitor wallet balance)" -ForegroundColor Blue
$taskBody = @{
    task_type = "monitor_wallet"
    wallet_address = "0x1234567890abcdef"
    description = "Monitor wallet balance"
} | ConvertTo-Json

$taskResponse = Invoke-RestMethod -Uri "$API_URL/task/start" -Method Post -Body $taskBody -ContentType "application/json"
$taskResponse | ConvertTo-Json -Depth 10

$TASK_ID = $taskResponse.task_id
Write-Host ""
Write-Host "Task ID: $TASK_ID" -ForegroundColor Green
Write-Host ""

Start-Sleep -Seconds 2

Write-Host "Step 2: Checking task status" -ForegroundColor Blue
$statusResponse = Invoke-RestMethod -Uri "$API_URL/task/$TASK_ID" -Method Get
$statusResponse | ConvertTo-Json -Depth 10

Write-Host ""
Start-Sleep -Seconds 2

Write-Host "Step 3: Waiting for approval (if required)..." -ForegroundColor Blue
Start-Sleep -Seconds 3

Write-Host "Step 4: Approving task" -ForegroundColor Yellow
$approvalBody = @{
    approved = $true
    reason = "Approved for execution"
} | ConvertTo-Json

$approvalResponse = Invoke-RestMethod -Uri "$API_URL/task/$TASK_ID/approve" -Method Post -Body $approvalBody -ContentType "application/json"
$approvalResponse | ConvertTo-Json -Depth 10

Write-Host ""
Start-Sleep -Seconds 3

Write-Host "Step 5: Checking final task status" -ForegroundColor Blue
$finalStatus = Invoke-RestMethod -Uri "$API_URL/task/$TASK_ID" -Method Get
$finalStatus | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "Step 6: Viewing audit log" -ForegroundColor Blue
$auditLog = Invoke-RestMethod -Uri "$API_URL/audit/$TASK_ID" -Method Get
$auditLog | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "Demo completed!" -ForegroundColor Green

