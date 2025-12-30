# Enhanced Live Monitor with Colors
# This version color-codes the output for easy scanning

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Parallel LLM MCP - Live Monitor" -ForegroundColor Cyan
Write-Host "  (Color-Coded)" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Watching: parallel_llm_progress.log" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
Write-Host ""
Write-Host "Legend:" -ForegroundColor White
Write-Host "  " -NoNewline; Write-Host "GREEN" -ForegroundColor Green -NoNewline; Write-Host "   = Success/Complete"
Write-Host "  " -NoNewline; Write-Host "YELLOW" -ForegroundColor Yellow -NoNewline; Write-Host "  = Starting/In Progress"
Write-Host "  " -NoNewline; Write-Host "RED" -ForegroundColor Red -NoNewline; Write-Host "     = Errors"
Write-Host "  " -NoNewline; Write-Host "MAGENTA" -ForegroundColor Magenta -NoNewline; Write-Host " = Timeouts/Warnings"
Write-Host "  " -NoNewline; Write-Host "CYAN" -ForegroundColor Cyan -NoNewline; Write-Host "    = Phase Headers"
Write-Host ""

$logFile = "parallel_llm_progress.log"

# Create log file if it doesn't exist
if (-not (Test-Path $logFile)) {
    New-Item -Path $logFile -ItemType File -Force | Out-Null
    Write-Host "Created new log file: $logFile" -ForegroundColor Green
    Write-Host ""
}

# Watch the log file with color coding
Get-Content -Path $logFile -Wait -Tail 50 | ForEach-Object {
    $line = $_
    
    # Color code based on content
    if ($line -match "ERROR|❌|✗|Failed") {
        Write-Host $line -ForegroundColor Red
    }
    elseif ($line -match "✅|COMPLETE|🎉|SUCCESS|Successfully") {
        Write-Host $line -ForegroundColor Green
    }
    elseif ($line -match "🚀|⚡|Starting|NEW REQUEST") {
        Write-Host $line -ForegroundColor Yellow
    }
    elseif ($line -match "⏱️|Timeout|WARN") {
        Write-Host $line -ForegroundColor Magenta
    }
    elseif ($line -match "PHASE|====") {
        Write-Host $line -ForegroundColor Cyan
    }
    elseif ($line -match "🔄|💾|📊|📋") {
        Write-Host $line -ForegroundColor White
    }
    else {
        Write-Host $line -ForegroundColor Gray
    }
}
