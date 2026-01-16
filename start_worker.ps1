# Start Celery Worker for Windows with Autoscaling
# Run this script to start the Celery worker

Write-Host "🚀 Starting Celery Worker with Autoscaling..." -ForegroundColor Green
Write-Host ""

# Check if Redis is running
$redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet
if (-not $redisRunning) {
    Write-Host "❌ Redis is not running on port 6379" -ForegroundColor Red
    Write-Host "Please start Redis first:" -ForegroundColor Yellow
    Write-Host "  - Run: redis-server" -ForegroundColor Yellow
    Write-Host "  - Or: net start Redis" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Redis is running" -ForegroundColor Green
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

$minConcurrency = [math]::Max(5, [math]::Floor($maxConcurrency / 4))

Write-Host "📊 Worker Configuration:" -ForegroundColor Cyan
Write-Host "   Pool Type: threads (Windows compatible)" -ForegroundColor White
Write-Host "   Max Concurrency: $maxConcurrency tasks" -ForegroundColor White
Write-Host "   Min Concurrency: $minConcurrency tasks" -ForegroundColor White
Write-Host "   Autoscaling: Enabled" -ForegroundColor Green
Write-Host ""

# Start Celery worker with autoscaling using threads pool
Write-Host "Starting Celery worker..." -ForegroundColor Cyan
celery -A celery_app worker --loglevel=info --pool=threads --autoscale=$maxConcurrency,$minConcurrency

# Note: --pool=threads is used for Windows with true concurrency
# --pool=solo only supports 1 task at a time (no concurrency)
# For production on Linux, use: --pool=prefork
# Autoscale format: --autoscale=MAX,MIN
