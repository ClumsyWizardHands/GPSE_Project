# PowerShell script to run GPSE with fixed memory
# Updated version that runs main_crew_fixed_memory.py

Write-Host "`nGPSE Terminal Runner" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "With comprehensive agent quality enhancements" -ForegroundColor Yellow
Write-Host "Memory FIXED with environment variable override" -ForegroundColor Cyan
Write-Host ""

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

Write-Host "`nRunning GPSE with fixed memory configuration..." -ForegroundColor Green
Write-Host ""

# Run the main crew with FIXED memory
python main_crew_fixed_memory.py

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

# Keep the window open
Read-Host "`nPress Enter to exit"
