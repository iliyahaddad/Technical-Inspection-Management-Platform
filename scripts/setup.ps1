# Setup Script for Windows
# Run this script in an Administrator PowerShell to prepare the development environment.

param(
    [switch]$SkipTools,
    [switch]$SkipDocker
)

$ErrorActionPreference = 'Stop'

Write-Host "=== Technical Inspection Platform Setup ===" -ForegroundColor Cyan

if (-not $SkipTools) {
    Write-Host "`n[1/4] Checking tooling..." -ForegroundColor Yellow
    $tools = @{ 'python' = 'python --version'; 'node' = 'node --version'; 'npm' = 'npm --version'; 'git' = 'git --version' }
    foreach ($tool in $tools.Keys) {
        $version = & $tools[$tool] 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Installing $tool..." -ForegroundColor Yellow
            winget install --id ($tool == 'python' ? 'Python.Python.3.12' : ($tool == 'node' ? 'OpenJS.NodeJS.LTS' : 'Git.Git')) --accept-package-agreements --accept-source-agreements
        } else {
            Write-Host "$tool found: $version" -ForegroundColor Green
        }
    }
}

if (-not $SkipDocker) {
    Write-Host "`n[2/4] Docker Desktop is required for containerized deployment." -ForegroundColor Yellow
    Write-Host "Download from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
}

Write-Host "`n[3/4] Initializing project..." -ForegroundColor Yellow
$projectDir = "C:\Users\manshadi.PDF\Desktop\technical inspection"
Set-Location $projectDir

if (-not (Test-Path ".git")) { git init }

Write-Host "`n[4/4] Creating Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "backend\.venv")) {
    python -m venv backend\.venv
    .\backend\.venv\Scripts\Activate.ps1
    pip install --upgrade pip
    pip install -r backend\requirements\development.txt
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit backend\.env with your database credentials"
Write-Host "2. Run: docker compose up --build (if Docker is available)"
Write-Host "3. Or run locally: cd backend && python manage.py migrate && python manage.py createsuperuser && python manage.py runserver"
Write-Host "4. Frontend: cd frontend && npm install && npm run dev"
