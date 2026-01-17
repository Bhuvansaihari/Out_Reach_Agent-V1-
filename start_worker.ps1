# Start Celery Worker for Windows
# Run this script to start the Celery worker

Write-Host "[*] Starting Celery Worker..." -ForegroundColor Green
Write-Host ""

# Check if Redis is running
$redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet
if (-not $redisRunning) {
    Write-Host "[X] Redis is not running on port 6379" -ForegroundColor Red
    Write-Host "Please start Redis first:" -ForegroundColor Yellow
    Write-Host "  - Run: redis-server" -ForegroundColor Yellow
    Write-Host "  - Or: net start Redis" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Redis is running" -ForegroundColor Green
Write-Host ""

# Load environment variables to get concurrency setting
$envFile = ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^CELERY_WORKER_CONCURRENCY=(.+)$') {
            $maxConcurrency = $matches[1]
        }
    }
}

# Default to 20 if not set
if (-not $maxConcurrency) {
    $maxConcurrency = 20
}

Write-Host "Worker Configuration:" -ForegroundColor Cyan
Write-Host "   Pool Type: threads (Windows compatible)" -ForegroundColor White
Write-Host "   Concurrency: $maxConcurrency threads" -ForegroundColor White
Write-Host ""

# Start Celery worker with fixed concurrency using threads pool
Write-Host "Starting Celery worker..." -ForegroundColor Cyan
# Uses $PID to create a unique name for each worker instance
celery -A celery_app worker --loglevel=info --pool=threads --concurrency=$maxConcurrency -n worker-$PID@%h

# Note: --pool=threads is used for Windows with true concurrency
# --pool=solo only supports 1 task at a time (no concurrency)
# For production on Linux, use: --pool=prefork
# Autoscale is NOT compatible with thread pool, use fixed --concurrency instead
