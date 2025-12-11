# Start Flower Monitoring UI for Windows
# Run this script to start the Flower web interface

Write-Host "🌸 Starting Flower Monitoring UI..." -ForegroundColor Magenta
Write-Host ""

# Check if Redis is running
$redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet
if (-not $redisRunning) {
    Write-Host "❌ Redis is not running on port 6379" -ForegroundColor Red
    Write-Host "Please start Redis first" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Redis is running" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Flower will be available at: http://localhost:5555" -ForegroundColor Cyan
Write-Host ""

# Start Flower
celery -A celery_app flower --port=5555
