# Comprehensive System Test Script
# Tests all services and features

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Qubic System Comprehensive Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$passed = 0
$failed = 0

function Test-Service {
    param(
        [string]$Name,
        [string]$Url,
        [string]$ExpectedStatus = "healthy"
    )
    
    Write-Host "Testing $Name..." -ForegroundColor Yellow -NoNewline
    try {
        $response = Invoke-RestMethod -Uri $Url -Method Get -ErrorAction Stop
        if ($response.status -eq $ExpectedStatus) {
            Write-Host " [PASSED]" -ForegroundColor Green
            $script:passed++
            return $true
        } else {
            Write-Host " [FAILED] Status: $($response.status)" -ForegroundColor Red
            $script:failed++
            $script:errors += "$Name returned status: $($response.status)"
            return $false
        }
    } catch {
        Write-Host " [FAILED] $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
        $script:errors += "$Name error: $($_.Exception.Message)"
        return $false
    }
}

# Test 1: Health Checks
Write-Host "=== Health Checks ===" -ForegroundColor Cyan
Test-Service "API Gateway" "http://localhost:8000/health"
Test-Service "Qubic Service" "http://localhost:8001/health"
Test-Service "Audit Service" "http://localhost:8002/health"
Test-Service "Worker Service" "http://localhost:8003/health"
Test-Service "Planner Service" "http://localhost:8004/health"
Test-Service "Agent Runtime" "http://localhost:8005/health"
Write-Host ""

# Test 2: Qubic Service Features
Write-Host "=== Qubic Service Features ===" -ForegroundColor Cyan

Write-Host "Testing Qubic Policy Check..." -ForegroundColor Yellow -NoNewline
try {
    $policy = Invoke-RestMethod -Uri "http://localhost:8001/policy?action_type=monitoring" -Method Get
    if ($policy.allowed -eq $true) {
        Write-Host " [PASSED]" -ForegroundColor Green
        $passed++
    } else {
        Write-Host " [FAILED]" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host " [FAILED]" -ForegroundColor Red
    $failed++
}

Write-Host "Testing Qubic Policies List..." -ForegroundColor Yellow -NoNewline
try {
    $policies = Invoke-RestMethod -Uri "http://localhost:8001/policies" -Method Get
    $policyCount = $policies.policies.Count
    if ($policyCount -gt 0) {
        Write-Host " [PASSED] ($policyCount policies)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host " [FAILED]" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host " [FAILED]" -ForegroundColor Red
    $failed++
}
Write-Host ""

# Test 3: Planner Service
Write-Host "=== Planner Service Features ===" -ForegroundColor Cyan

Write-Host "Testing Plan Creation..." -ForegroundColor Yellow -NoNewline
try {
    $planRequest = @{
        task_id = "test-task-123"
        task_type = "monitor_wallet"
        description = "Test monitoring"
        parameters = @{
            wallet_address = "0x1234567890abcdef"
        }
    } | ConvertTo-Json
    
    $plan = Invoke-RestMethod -Uri "http://localhost:8004/plan/create" -Method Post -Body $planRequest -ContentType "application/json"
    if ($plan.plan_id -and $plan.steps.Count -gt 0) {
        $stepCount = $plan.steps.Count
        Write-Host " [PASSED] Plan ID: $($plan.plan_id), Steps: $stepCount" -ForegroundColor Green
        $passed++
        $testPlanId = $plan.plan_id
        
        # Test getting plan
        Write-Host "Testing Plan Retrieval..." -ForegroundColor Yellow -NoNewline
        try {
            $retrievedPlan = Invoke-RestMethod -Uri "http://localhost:8004/plan/$testPlanId" -Method Get
            if ($retrievedPlan.plan_id -eq $testPlanId) {
                Write-Host " [PASSED]" -ForegroundColor Green
                $passed++
            } else {
                Write-Host " [FAILED]" -ForegroundColor Red
                $failed++
            }
        } catch {
            Write-Host " [FAILED]" -ForegroundColor Red
            $failed++
        }
    } else {
        Write-Host " [FAILED]" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host " [FAILED] $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}
Write-Host ""

# Test 4: Complete Task Workflow
Write-Host "=== Complete Task Workflow ===" -ForegroundColor Cyan

Write-Host "Step 1: Creating Task..." -ForegroundColor Yellow -NoNewline
try {
    $taskRequest = @{
        task_type = "monitor_wallet"
        wallet_address = "0x1234567890abcdef"
        description = "Monitor wallet balance test"
    } | ConvertTo-Json
    
    $task = Invoke-RestMethod -Uri "http://localhost:8000/task/start" -Method Post -Body $taskRequest -ContentType "application/json"
    if ($task.task_id) {
        Write-Host " [PASSED] Task ID: $($task.task_id)" -ForegroundColor Green
        $passed++
        $testTaskId = $task.task_id
        
        Write-Host "Step 2: Checking Task Status..." -ForegroundColor Yellow -NoNewline
        Start-Sleep -Seconds 3
        try {
            $status = Invoke-RestMethod -Uri "http://localhost:8000/task/$testTaskId" -Method Get
            if ($status.task_id -eq $testTaskId) {
                Write-Host " [PASSED] Status: $($status.status)" -ForegroundColor Green
                $passed++
                
                # Test approval if needed
                if ($status.requires_approval) {
                    Write-Host "Step 3: Approving Task..." -ForegroundColor Yellow -NoNewline
                    try {
                        $approvalRequest = @{
                            approved = $true
                            reason = "Test approval"
                        } | ConvertTo-Json
                        
                        $approval = Invoke-RestMethod -Uri "http://localhost:8000/task/$testTaskId/approve" -Method Post -Body $approvalRequest -ContentType "application/json"
                        Write-Host " [PASSED]" -ForegroundColor Green
                        $passed++
                    } catch {
                        Write-Host " [FAILED]" -ForegroundColor Red
                        $failed++
                    }
                }
                
                # Test audit log
                Write-Host "Step 4: Checking Audit Log..." -ForegroundColor Yellow -NoNewline
                Start-Sleep -Seconds 5
                try {
                    $audit = Invoke-RestMethod -Uri "http://localhost:8000/audit/$testTaskId" -Method Get
                    if ($audit.task_id -eq $testTaskId) {
                        $logCount = $audit.logs.Count
                        Write-Host " [PASSED] Logs: $logCount" -ForegroundColor Green
                        $passed++
                        
                        # Test Qubic verification if we have a hash
                        if ($logCount -gt 0 -and $audit.logs[0].output_hash) {
                            Write-Host "Step 5: Verifying Hash in Qubic..." -ForegroundColor Yellow -NoNewline
                            try {
                                $hash = $audit.logs[0].output_hash
                                $verify = Invoke-RestMethod -Uri "http://localhost:8001/verify/$hash" -Method Get
                                if ($verify.verified) {
                                    Write-Host " [PASSED] TXID: $($verify.txid)" -ForegroundColor Green
                                    $passed++
                                } else {
                                    Write-Host " [FAILED] Hash not verified" -ForegroundColor Red
                                    $failed++
                                }
                            } catch {
                                Write-Host " [FAILED]" -ForegroundColor Red
                                $failed++
                            }
                        }
                    } else {
                        Write-Host " [FAILED]" -ForegroundColor Red
                        $failed++
                    }
                } catch {
                    Write-Host " [FAILED] $($_.Exception.Message)" -ForegroundColor Red
                    $failed++
                }
            } else {
                Write-Host " [FAILED]" -ForegroundColor Red
                $failed++
            }
        } catch {
            Write-Host " [FAILED] $($_.Exception.Message)" -ForegroundColor Red
            $failed++
        }
    } else {
        Write-Host " [FAILED]" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host " [FAILED] $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}
Write-Host ""

# Test 5: Direct Service Endpoints
Write-Host "=== Direct Service Endpoints ===" -ForegroundColor Cyan

Write-Host "Testing Agent Runtime Status..." -ForegroundColor Yellow -NoNewline
try {
    # This might fail if no tasks are running, which is OK
    $runtimeStatus = Invoke-RestMethod -Uri "http://localhost:8005/task/test-task-123/status" -Method Get -ErrorAction SilentlyContinue
    Write-Host " [PASSED] Endpoint accessible" -ForegroundColor Green
    $passed++
} catch {
    # 404 is expected if task doesn't exist
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host " [PASSED] Endpoint accessible (404 expected)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host " [FAILED]" -ForegroundColor Red
        $failed++
    }
}

Write-Host "Testing Worker Service Execution..." -ForegroundColor Yellow -NoNewline
try {
    $execRequest = @{
        task_id = "test-exec-123"
        step = @{
            step_id = "1"
            type = "check_balance"
            parameters = @{
                wallet_address = "0x1234567890abcdef"
            }
        }
        context = @{}
    } | ConvertTo-Json
    
    $execResult = Invoke-RestMethod -Uri "http://localhost:8003/execute" -Method Post -Body $execRequest -ContentType "application/json"
    if ($execResult.status -eq "success" -and $execResult.input_hash) {
        $hashPrefix = $execResult.input_hash.Substring(0,16)
        Write-Host " [PASSED] Hash: $hashPrefix..." -ForegroundColor Green
        $passed++
    } else {
        Write-Host " [FAILED]" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host " [FAILED] $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($errors.Count -gt 0) {
    Write-Host "Errors:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
}

if ($failed -eq 0) {
    Write-Host "[SUCCESS] All tests passed! System is fully operational." -ForegroundColor Green
} else {
    Write-Host "[WARNING] Some tests failed. Please check the errors above." -ForegroundColor Red
}

