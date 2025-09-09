# TimeCraft Environment Setup (PowerShell)
# Ensures conda environment and dependencies are properly installed

Write-Host "🚀 TimeCraft Environment Setup (PowerShell)" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

function Invoke-SafeCommand($command) {
    try {
        Invoke-Expression $command
        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-Host "Error running: $command" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $false
    }
}

# Check if conda is installed
if (-not (Test-Command "conda")) {
    Write-Host "❌ Conda is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Miniconda or Anaconda first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Conda is installed" -ForegroundColor Green

# Check if environment exists
$envExists = $false
try {
    $envList = conda env list --json | ConvertFrom-Json
    $envExists = $envList.envs | Where-Object { $_ -like "*timecraft*" }
}
catch {
    Write-Host "Warning: Could not check existing environments" -ForegroundColor Yellow
}

if ($envExists) {
    Write-Host "✅ Conda environment 'timecraft' already exists" -ForegroundColor Green
    Write-Host "📦 Updating conda environment..." -ForegroundColor Cyan
    
    if (-not (Invoke-SafeCommand "conda env update -f environment.yml --prune")) {
        Write-Host "⚠️  Warning: Failed to update conda environment" -ForegroundColor Yellow
    }
}
else {
    Write-Host "📦 Creating new conda environment..." -ForegroundColor Cyan
    
    if (-not (Invoke-SafeCommand "conda env create -f environment.yml")) {
        Write-Host "❌ Failed to create conda environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Conda environment created successfully" -ForegroundColor Green
}

# Install BRIDGE requirements
if (Test-Path "BRIDGE\requirements.txt") {
    Write-Host "📦 Installing BRIDGE requirements..." -ForegroundColor Cyan
    
    if (-not (Invoke-SafeCommand "conda run -n timecraft pip install -r BRIDGE\requirements.txt")) {
        Write-Host "⚠️  Warning: Failed to install BRIDGE requirements" -ForegroundColor Yellow
    }
    else {
        Write-Host "✅ BRIDGE requirements installed" -ForegroundColor Green
    }
}

# Install additional packages
Write-Host "📦 Installing additional packages..." -ForegroundColor Cyan
$additionalPackages = @("fastapi", "uvicorn", "python-multipart", "jinja2", "aiofiles")

foreach ($package in $additionalPackages) {
    if (-not (Invoke-SafeCommand "conda run -n timecraft pip install $package")) {
        Write-Host "⚠️  Warning: Failed to install $package" -ForegroundColor Yellow
    }
}

Write-Host "✅ Additional packages installed" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the environment manually:" -ForegroundColor Cyan
Write-Host "  conda activate timecraft" -ForegroundColor White
Write-Host ""
Write-Host "To run TimeCraft:" -ForegroundColor Cyan
Write-Host "  Press F5 in VS Code and select 'TimeCraft Full Stack'" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue"
