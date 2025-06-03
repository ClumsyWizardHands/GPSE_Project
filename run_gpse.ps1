# PowerShell script to run GPSE FINAL FIXED VERSION in a clean environment
# This version fixes the double path and missing analysis_id issues

Write-Host "`nGPSE Terminal Runner - FINAL FIXED VERSION" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Fixes applied:" -ForegroundColor Yellow
Write-Host "- Double path issue (strategy_analyses/strategy_analyses/...)" -ForegroundColor Yellow
Write-Host "- Missing analysis_id KeyError" -ForegroundColor Yellow
Write-Host "- Result logging errors`n" -ForegroundColor Yellow

# Navigate to project directory
Set-Location "C:\Users\every\Desktop\GPSE_Project"

# Check if virtual environment exists
if (Test-Path ".\gpse_venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & .\gpse_venv\Scripts\Activate.ps1
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv gpse_venv
    & .\gpse_venv\Scripts\Activate.ps1
    
    Write-Host "Installing requirements..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

Write-Host "`nRunning GPSE with all fixes..." -ForegroundColor Green
Write-Host ""

# Run the final fixed version
python run_gpse_final.py

Write-Host "`nExecution complete!" -ForegroundColor Green

# Option to view the created file
$analysisFile = "strategy_analyses\GGSM-$(Get-Date -Format 'MMddyy')-DailyAnalysis.md"
if (Test-Path $analysisFile) {
    Write-Host "`nAnalysis file created: $analysisFile" -ForegroundColor Green
    $response = Read-Host "`nWould you like to open the analysis file? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Start-Process notepad.exe $analysisFile
    }
}
