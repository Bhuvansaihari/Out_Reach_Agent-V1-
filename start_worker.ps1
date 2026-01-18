# Start Celery Worker for Windows
# Run this script to start the Celery worker

Write-Host "[*] Starting Celery Worker..." -ForegroundColor Green
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

# Notes:
# --pool=threads is used for Windows with true concurrency
# --pool=solo only supports 1 task at a time (no concurrency)
# For production on Linux, use: --pool=prefork
# Redis connectivity is handled via environment variables (Azure Cache for Redis in prod)
