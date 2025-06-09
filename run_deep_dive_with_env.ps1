<#
.SYNOPSIS
    Runs GPSE Deep Dive Analysis with environment variables from .env file
.DESCRIPTION
    This script loads environment variables from the .env file and executes
    the GPSE Deep Dive Analysis that produces both executive brief and regional analyses
#>

Write-Host "================================" -ForegroundColor Cyan
Write-Host "GPSE Deep Dive Analysis Launcher" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check and activate virtual environment if available
if (Test-Path ".\gpse_venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\gpse_venv\Scripts\Activate.ps1"
    Write-Host "Virtual environment activated!" -ForegroundColor Green
} else {
    Write-Host "No virtual environment found, using system Python" -ForegroundColor Yellow
}

# Function to load .env file
function Load-EnvFile {
    param([string]$EnvFile = ".env")
    
    if (Test-Path $EnvFile) {
        Write-Host "Loading environment variables from $EnvFile..." -ForegroundColor Yellow
        
        Get-Content $EnvFile | ForEach-Object {
            if ($_ -match '^[^#].*=.*$') {
                $parts = $_ -split '=', 2
                if ($parts.Count -eq 2) {
                    $name = $parts[0].Trim()
                    $value = $parts[1].Trim()
                    # Remove surrounding quotes if present
                    if ($value.StartsWith('"') -and $value.EndsWith('"')) {
                        $value = $value.Substring(1, $value.Length - 2)
                    } elseif ($value.StartsWith("'") -and $value.EndsWith("'")) {
                        $value = $value.Substring(1, $value.Length - 2)
                    }
                    [Environment]::SetEnvironmentVariable($name, $value, [System.EnvironmentVariableTarget]::Process)
                    Write-Host "  ✓ Set $name" -ForegroundColor Green
                }
            }
        }
    } else {
        Write-Host "ERROR: .env file not found!" -ForegroundColor Red
        exit 1
    }
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found in PATH!" -ForegroundColor Red
    Write-Host "Please ensure Python is installed and added to PATH." -ForegroundColor Yellow
    exit 1
}

# Load environment variables
Load-EnvFile

# Verify critical API keys are set
$requiredKeys = @("OPENAI_API_KEY", "ANTHROPIC_API_KEY")
$missingKeys = @()

foreach ($key in $requiredKeys) {
    if (-not [Environment]::GetEnvironmentVariable($key)) {
        $missingKeys += $key
    }
}

if ($missingKeys.Count -gt 0) {
    Write-Host ""
    Write-Host "ERROR: Missing required API keys:" -ForegroundColor Red
    foreach ($key in $missingKeys) {
        Write-Host "  - $key" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Please ensure these keys are in your .env file." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "All required API keys loaded successfully!" -ForegroundColor Green
Write-Host ""

# Display what will be generated
Write-Host "This analysis will generate:" -ForegroundColor Cyan
Write-Host "1. Executive Brief (1-2 pages)"
Write-Host "2. Regional Deep Dives (5-10 pages each):"
Write-Host "   - Americas (North and South)"
Write-Host "   - Europe and Russia"
Write-Host "   - Middle East and North Africa"
Write-Host "   - Sub-Saharan Africa"
Write-Host "   - South and Central Asia"
Write-Host "   - East Asia and Pacific"
Write-Host "   - Global Threats and Non-State Actors"
Write-Host "3. Analysis Index linking all documents"
Write-Host ""
Write-Host "Estimated processing time: 10-20 minutes" -ForegroundColor Yellow
Write-Host ""

# Confirm execution
$response = Read-Host "Proceed with deep dive analysis? (y/n)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "Analysis cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Starting GPSE Deep Dive Analysis..." -ForegroundColor Green
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

# Run the deep dive analysis
try {
    # Change to the project directory to ensure relative paths work
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Push-Location $scriptDir
    
    # Execute the main script
    python main_crew_global_deep_dive.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================" -ForegroundColor Green
        Write-Host "✅ Deep Dive Analysis Complete!" -ForegroundColor Green
        Write-Host "================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Check the strategy_analyses/ directory for:" -ForegroundColor Cyan
        Write-Host "- Executive Brief" -ForegroundColor White
        Write-Host "- Regional Deep Dive files" -ForegroundColor White
        Write-Host "- Analysis Index" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "❌ Analysis failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Check the error messages above for details." -ForegroundColor Yellow
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error during execution:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Message -like "*permission*" -or $_.Exception.Message -like "*chromadb*") {
        Write-Host ""
        Write-Host "ChromaDB Error Detected!" -ForegroundColor Yellow
        Write-Host "Try these solutions:" -ForegroundColor Yellow
        Write-Host "1. Run PowerShell as Administrator" -ForegroundColor White
        Write-Host "2. Check if antivirus is blocking ChromaDB" -ForegroundColor White
        Write-Host "3. Use the no-memory version if issue persists" -ForegroundColor White
    }
} finally {
    # Return to original directory
    Pop-Location
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
