# Live Progress Monitor for Parallel LLM MCP Server
# This script watches the progress log file in real-time

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Parallel LLM MCP - Live Monitor" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Watching: parallel_llm_progress.log" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
Write-Host ""

$logFile = "parallel_llm_progress.log"

# Create log file if it doesn't exist
if (-not (Test-Path $logFile)) {
    New-Item -Path $logFile -ItemType File -Force | Out-Null
    Write-Host "Created new log file: $logFile" -ForegroundColor Green
}

# Watch the log file in real-time
Get-Content -Path $logFile -Wait -Tail 50
